echo "Installing deployment requirements."
 conda install conda-build anaconda-client

if [[ "$TRAVIS_TAG" == v* ]]; then

  file_to_upload=$(conda build --output --python=$TRAVIS_PYTHON_VERSION --numpy=$NUMPY_VERSION .conda)

  echo "Building conda package"
  conda build .conda -c landlab > stdout || exit -1

  echo "Uploading to Anaconda"
  anaconda -t $ANACONDA_TOKEN upload --force --user landlab --channel main $file_to_upload

  echo "Done."
else
  export BUILD_STR='dev'

  file_to_upload=$(conda build --output --python=$TRAVIS_PYTHON_VERSION --numpy=$NUMPY_VERSION .conda)

  echo "Building conda package"
  conda build .conda -c landlab > stdout || exit -1

  echo "Uploading to Anaconda"
  anaconda -t $ANACONDA_TOKEN upload --force --user landlab --channel $BUILD_STR $file_to_upload

  echo "Done."
  echo "Not deploying."
  echo "Tag is... $TRAVIS_TAG"
  echo "Branch name is... $TRAVIS_BRANCH"
fi
