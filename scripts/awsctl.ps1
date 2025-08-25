param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $Args
)

$workdir = "$PWD"
$home = "$env:USERPROFILE"

docker run --rm -it `
  -v "$workdir:/work" -w /work `
  -v "$home:/root" `
  --entrypoint awsctl `
  awsctl:latest $Args
