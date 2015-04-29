## Creating a release of Tsammalex Data

1. Make sure the integrity checks for the data pass.
2. Enrich the taxon data from external sources running the `updatetaxa` command.
3. Git add, commit and push the updated taxon data.
4. Upload images to the MPG imeji repository.
5. Git commit and push the updated image data.
6. [Create a release](https://help.github.com/articles/creating-releases/) of the repository.
7. [Import the release](https://github.com/clld/tsammalex/blob/master/RELEASE.md) in http://tsammalex.clld.org
