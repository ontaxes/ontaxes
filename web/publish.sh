#!/usr/bin/env bash

npm run build
git add .
git commit -m "rebuild"
git subtree push --prefix web/dist origin gh-pages