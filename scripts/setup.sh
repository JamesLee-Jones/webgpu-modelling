set -e
set -u
set -x

# Check the script is being called from the repository root.
test -d ./AlloyModel
test -d ./test
test -d ./scripts
test -d ./third_party

wget -P ./third_party https://github.com/AlloyTools/org.alloytools.alloy/releases/download/v6.0.0/org.alloytools.alloy.dist.jar