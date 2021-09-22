features = [
    "Add one feature here",
    "Add another feature here",
    "And so on",
]

optional_and_languages = [
    "Optional",
    "Go",
    "Java",
    "JS",
    "Python",
    "Ruby",
    "Erlang",
    "PHP",
    "Rust",
    "C++",
    ".NET",
    "Swift",
]

max_feature_length = max(map(len, features))

print(
    f"| Feature {' ' * (max_feature_length - 8)} | "
    f"{' | '.join(word for word in optional_and_languages)} |"
)
print(
    f"|{'-' * (max_feature_length + 2)}|-"
    f"{'-|-'.join('-' * len(word) for word in optional_and_languages)}-|"
)

for feature in features:
    print(
        f"| {feature}{' ' * (max_feature_length - len(feature))} | "
        f"{' | '.join(' ' * len(word) for word in optional_and_languages)} |"
    )
