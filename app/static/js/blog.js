$(document).ready(function () {
    // Js works in blog categories page
    if (window.location.pathname.indexOf($BLOG_CATEGORY_PATH) > -1) {
        var childCategory = $('.child-category');
        childCategory.on('click', function () {
            window.location.replace($SCRIPT_ROOT + $(this).children('a').attr('href'))
        });

        childCategory.on('mouseover', function () {
            // $(this).prop('style', 'box-shadow: rgb(245, 245, 245) -1px -1px 5px;');
            $(this).children('a').prop('style', 'color:rgb(55,55,55);')
        });

        childCategory.on('mouseout', function () {
            // $(this).prop('style', 'box-shadow: none;');
            $(this).children('a').prop('style', 'color:dimgray')

        });
    }

    // resize code element when use pygments to highlight code
    if ($READING_BLOG) {
        var code_table = $(".highlighttable");
        var post_content = $(".post-content");
        code_table.each(function (index) {
            var line_no = $(this).find("td.linenos").eq(-1);
            var code_pr = $(this).find("td.code").eq(-1);
            var code_hl = code_pr.find("div.highlight").eq(-1);
            line_no.css({"float": "left"});
            code_hl.width(post_content.width() - line_no.width() - 5);
            line_no.find(".linenodiv").eq(-1).height(code_hl.height());
            line_no.find("pre").eq(-1).css({"height": "100%"})
        })
    }

});