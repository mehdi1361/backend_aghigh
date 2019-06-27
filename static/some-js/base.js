var image_load = function (el, load) {
    $(el).removeClass('hide').parents('.image_loader').addClass(load ? 'load' : 'no-load');
    $(el).siblings('.image-loader').remove();

    var target = $(el).data('target');
    if (target === undefined) return;
    var set = null;
    if (target === 'parent') set = $(el).parent();
    else {
        if (target === 'image_set') set = $(el).siblings('.image_set');
        else set = $(target);
    }
    var src = $(el).attr('src');
    set.attr('style', 'background-image:url("' + src + '")');
};