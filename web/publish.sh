#!/usr/bin/env bash

npm run build
cd ..
git add .
git commit -m "rebuild"
git subtree push --prefix web/dist origin gh-pages