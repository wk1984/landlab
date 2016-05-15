if [[ "$TRAVIS_TAG" == v* ]]; then
  echo "Building release version"
  unset BUILD_STR
  export CHANNEL="main"
else
  echo "Building dev version"
  export BUILD_STR="dev"
  export CHANNEL="dev"
fi
echo "Building package for Python $PYTHON_VERSION, numpy $NUMPY_VERSION"
conda config --set anaconda_upload no

file_to_upload=$(conda build --output .conda)
file_to_upload=$(echo $file_to_upload | rev | cut -d ' ' -f 1 | rev)

# echo "Building conda package"
# conda build .conda -c landlab || exit -1

echo "Uploading $file_to_upload to $CHANNEL"
anaconda -t $ANACONDA_TOKEN upload --force --user landlab --channel $CHANNEL $file_to_upload

echo "Done."
