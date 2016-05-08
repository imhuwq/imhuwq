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
    
});