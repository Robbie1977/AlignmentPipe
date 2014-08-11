function appendObjectTools(tools) {
    /* Appends items to the object tool list.
     *
     * 'tools' param is an Array of Objects in which each Object
     * has 'url' and 'title' properties corresponding to the
     * URL and href for each link.
     * Ref: http://fragmentsofcode.wordpress.com/2008/12/10/adding-object-tools-to-django-admin-pages/
     */
    html = '';
    for (var i=0; i < tools.length; i++) {
	html += '<li><a href="' + tools[i].url + '">' + tools[i].title + '</a></li>';
    }
    $('#content-main .object-tools').append(html);
}
