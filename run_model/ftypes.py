from dataclasses import dataclass

# Define NamedTuple classes for download and invoke arguments
@dataclass
class DownloadArgs():
    repo_name: str
    file_name: str

    def __post_init__(self):
        self.repo_name_dir = self.repo_name.replace("/", "-")

@dataclass
class InvokeArgs():
    repo_name: str
    file_name: str
    prompt: str
    model_type: str
    context_length: int = 512

    def __post_init__(self):
        self.repo_name_dir = self.repo_name.replace("/", "-")