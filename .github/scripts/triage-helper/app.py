import os
import argparse
from github import Github
from datetime import datetime, timedelta
import pytz
from operator import attrgetter

def is_meaningful_activity(item):
    if isinstance(item, dict):  # Comment
        return True
    meaningful_events = [
        "committed",
        "commented",
        "merged",
        "referenced",
        "closed",
        "reopened"
    ]
    return item.event in meaningful_events or (
        item.event in ["labeled", "unlabeled"] and
        (item.label.name.startswith("triage:deciding") or item.label.name == "triage:followup")
    )

def get_timeline(issue):
    timeline = []

    # Add events
    for event in issue.get_events():
        timeline.append({
            'type': 'event',
            'created_at': event.created_at,
            'event': event,
        })

    # Add comments
    for comment in issue.get_comments():
        timeline.append({
            'type': 'comment',
            'created_at': comment.created_at,
            'comment': comment,
        })

    return sorted(timeline, key=lambda x: x['created_at'])

def needs_followup(issue, verbose=False):
    now = datetime.now(pytz.UTC)
    two_weeks_ago = now - timedelta(weeks=2)

    timeline = get_timeline(issue)

    if verbose:
        print(f"Analyzing issue #{issue.number}: {issue.title}")
        print(f"Current time: {now}")
        print(f"Two weeks ago: {two_weeks_ago}")
        print("Timeline:")
        for item in timeline:
            if item['type'] == 'event':
                event = item['event']
                print(f"  {item['created_at']}: Event - {event.event}" + (f" - {event.label.name}" if event.event in ['labeled', 'unlabeled'] else ""))
            else:
                comment = item['comment']
                print(f"  {item['created_at']}: Comment by {comment.user.login}")

    deciding_label_added = None
    followup_label_removed = None
    last_meaningful_activity = None

    for item in timeline:
        item_time = item['created_at'].replace(tzinfo=pytz.UTC)

        if item['type'] == 'event':
            event = item['event']
            if event.event == "labeled" and event.label.name.startswith("triage:deciding"):
                deciding_label_added = item_time
            elif event.event == "unlabeled" and event.label.name == "triage:followup":
                followup_label_removed = item_time

        if is_meaningful_activity(item['event'] if item['type'] == 'event' else item):
            last_meaningful_activity = item_time

    if verbose:
        print(f"Deciding label added: {deciding_label_added}")
        print(f"Followup label removed: {followup_label_removed}")
        print(f"Last meaningful activity: {last_meaningful_activity}")

    # Decision making
    if not deciding_label_added or deciding_label_added > two_weeks_ago:
        return False
    if last_meaningful_activity == deciding_label_added:
        return False
    if last_meaningful_activity > deciding_label_added:
        return True
    if followup_label_removed and followup_label_removed < two_weeks_ago and last_meaningful_activity > followup_label_removed:
        return True

    return False

def add_followup_label(issue, dry_run=False):
    issue_url = issue.html_url
    issue_title = issue.title
    if dry_run:
        print(f"[DRY RUN] Would add 'triage:followup' label to issue #{issue.number}")
        print(f"           Title: {issue_title}")
        print(f"           URL: {issue_url}")
    else:
        try:
            issue.add_to_labels("triage:followup")
            print(f"Added 'triage:followup' label to issue #{issue.number}")
            print(f"Title: {issue_title}")
            print(f"URL: {issue_url}")
        except Exception as e:
            print(f"Error adding label to issue #{issue.number}: {str(e)}")
            print(f"Title: {issue_title}")
            print(f"URL: {issue_url}")

def main(repo_name, dry_run):
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("GitHub token not found. Set the GITHUB_TOKEN environment variable.")

    g = Github(github_token)
    repo = g.get_repo(repo_name)

    for issue in repo.get_issues(state="open"):
        if any(label.name.startswith("triage:deciding:") for label in issue.labels):
            if needs_followup(issue) and "triage:followup" not in [label.name for label in issue.labels]:
                add_followup_label(issue, dry_run)

def test_issue(repo_name, issue_number):
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("GitHub token not found. Set the GITHUB_TOKEN environment variable.")

    g = Github(github_token)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)

    print(f"Testing issue #{issue_number}")
    needs_followup(issue, verbose=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add followup labels to GitHub issues.")
    parser.add_argument("repo", help="The GitHub repository in the format 'owner/repo'")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without making changes")
    parser.add_argument("--test-issue", type=int, help="Test a specific issue number")
    args = parser.parse_args()

    if args.test_issue:
        test_issue(args.repo, args.test_issue)
    else:
        main(args.repo, args.dry_run)
