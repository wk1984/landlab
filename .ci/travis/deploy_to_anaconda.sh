if [[ "$TRAVIS_TAG" == v* ]]; then

  file_to_upload=$(conda build --output --python=$TRAVIS_PYTHON_VERSION --numpy=$NUMPY_VERSION .conda)

  echo "Building conda package"
  conda build .conda -c landlab > stdout || exit -1

  echo "Uploading to Anaconda"
  anaconda -t $ANACONDA_TOKEN upload --force --user landlab --channel main $file_to_upload

  echo "Done."
else
  file_to_upload=$(conda build --output --python=$TRAVIS_PYTHON_VERSION --numpy=$NUMPY_VERSION .conda)

  echo "Building conda package"
  conda build .conda -c landlab || exit -1

  echo "Uploading to Anaconda"
  echo anaconda -t $ANACONDA_TOKEN upload --force --user landlab --channel dev $file_to_upload
  anaconda -t $ANACONDA_TOKEN upload --force --user landlab --channel dev $file_to_upload

  echo "Done."
  echo "Not deploying."
  echo "Tag is... $TRAVIS_TAG"
  echo "Branch name is... $TRAVIS_BRANCH"
fi
