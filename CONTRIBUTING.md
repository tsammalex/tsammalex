## Contributing

<p>
    The expansion of the Tsammalex database strongly depends on researchers and communities willing
    to share their knowledge or collected data. If you are interested in a contribution and have
    questions, don't hesitate to
    <a href="http://tsammalex.clld.org/contact">contact</a> one of the editors
    (Christfried Naumann, Steven Moran or Robert Forkel).
</p>
<p>
    The structure of the database is based on
    <a href="http://en.wikipedia.org/wiki/Comma-separated_values" title="csv tables"><i class="icon-share"></i> csv tables</a>
    ("...csv"), i.e., a simple file format that can
    be opened and edited in editors such as Notepad, or calculation programs such as LibreOffice Calc or
    Microsoft Excel.
    <a href="https://github.com/clld/tsammalex-data/tree/master/tsammalexdata/data" title="These csv files"><i class="icon-share"></i> These csv files</a>
    contain all data on biological species and related linguistic or
    lexical data, as well as metadata of audio and image files, etc.
    There is
    <a href="https://github.com/clld/tsammalex-data/blob/master/tsammalexdata/data/sources.bib" title="a BibTeX"><i class="icon-share"></i> a BibTeX</a>
    file containing all
    references cited. Images of species (licensed as Creative Commons or in Public domain) might be
    uploaded to websites such as Flickr or Wikimedia Commons and linked, or sent to the editors.
    For more information on the structure of the data and on planned improvements refer to
    <a href="http://tsammalex.clld.org/static/Tsammalex-Manual.pdf">the manual [PDF]</a>.
</p>
<p>
    Contributions of data must be committed in the form of csv files. In a Windows environment, we recommend
    using LibreOffice Calc. Open the csv table templates, set the character encoding to UTF-8 (Unicode) and
    select comma separated table. Have a look into the sketch manual about obligatory vs. optional
    information, and start entering data. Send these files to the editors.
</p>
<p>
    Alternatively, if you feel comfortable with the
    <a href="https://help.github.com/articles/using-pull-requests/" title="GitHub collaboration model"><i class="icon-share"></i> GitHub collaboration model</a>
    you may fork the
    <a href="https://github.com/clld/tsammalex-data" title="tsammalex-data repository"><i class="icon-share"></i> tsammalex-data repository</a>,
    add your data and submit a pull request.
</p>
<p>
    Notes:
</p>
<ul>
    <li>Lexical data in "names.csv" must be associated with one species (or another biological taxon, such as a genus).</li>
    <li>Any species (or other taxon) referred to under "names.csv" must be included previously under "species.csv".</li>
    <li>
        The consistency of the data in the tsammalex-data repository is checked by
        <a href="https://travis-ci.org/clld/tsammalex-data" title="Travis-CI"><i class="icon-share"></i> Travis-CI</a>,
        so if you choose to add data using pull request, you get the added benefit of having your additions
        cross-checked while you are working on them.
    </li>
    <li>
        Further information on the rationale behind curating the data in this way are available
        in <a href="http://clld.org/2015/02/03/open-source-research-data.html" title="this post"><i class="icon-share"></i> this post</a>.
    </li>
</ul>
