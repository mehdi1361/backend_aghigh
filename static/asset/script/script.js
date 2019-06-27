var source = {
    body : $('body'),
    ready : function () {
        if(isMobile())
            source.body.addClass('mobile');
        else
            source.body.addClass('pc');

        set_persian();
        set_copy();
        set_btn();
        set_input();
        set_select();
        set_ranger();
        source.resize();
        set_weigth();
        set_tab();
        setTimeout(function () {
            set_slide();
            source.body.addClass('ready');
        },110);
    },
    load : function () {

        var el = $('#banner-image');
        var width = 190 - el.outerWidth();
        if(width < 0)
            width = width / 2;
        el.css('right', width + 'px');


        setTimeout(function () {
            $('[data-src]').each(function () {
                var src = $(this).data('src');
                $(this).attr('src', src).removeAttr('data-src');
            });
        },20);

        setTimeout(function () {
            source.body.addClass('load');
        },100);
    },
    resize : function () {
        setTimeout(function () {
            var height = document.body.clientHeight;
            var width = document.body.clientWidth;
            $('.body_height').css('height', height + 'px');
            $('.body_min_height').css('min-height', height + 'px');
            set_weigth();
        },100);
    },
    scroll : function () {

    }
};
$(window).resize(source.resize);
$(window).on('load',source.load);
$(window).scroll(source.scroll);
$(document).ready(source.ready);

/////////////////////////////////////////////////////////// event
$(document).on('click',function () {
    $('.form-group.focus').removeClass('focus');
});
$(document).on('focus','.form-control',function () {
    var el = $(this);
    $('.form-group.focus').removeClass('focus');
    if(el.attr('readonly') || el.attr('disabled')) return;
   setTimeout(function () {
       el.parents('.form-group').addClass('focus');
   },100);
});
$(document).on('change','.form-control',function () {
    check_input($(this));
});
$(document).on('click','.notification-item',function () {
    if(!$(this).hasClass('open'))
        $('.notification-item.open').removeClass('open');
    $(this).toggleClass('open').removeClass('new');
    var top = $(this).offset().top - 50;
    $('body,html').animate({scrollTop: top + 'px'}, 800);
});
/////////////////////////////////////////////////////////// helper
var set_persian = function () {
  $('.persian_number').each(function () {
      $(this).html(getArabicNumbers($(this).html())).removeClass('persian_number');
  })
};
var set_copy = function () {
  $('[data-copy]').each(function () {
     var el = $(this);
     var target = $(el.data('copy'));
     el.removeAttr('data-copy');
     target.html(el.html());
  });
};
var set_btn = function () {
    var taint, d, x, y;
    $(".btn").click(function(e){
        if ($(this).find(".taint").length == 0) {
            $(this).prepend("<span class='taint'></span>")
        }
        taint = $(this).find(".taint");
        taint.removeClass("drop");
        if(!taint.height() && !taint.width()) {
            d = Math.max($(this).outerWidth(), $(this).outerHeight());
            taint.css({height: d, width: d});
        }
        x = e.pageX - $(this).offset().left - taint.width()/2;
        y = e.pageY - $(this).offset().top - taint.height()/2;
        taint.css({top: y+'px', left: x+'px'}).addClass("drop");
    });
};
var set_input = function () {
    $('.form-control').each(function () {
        check_input($(this));
    });
};
var check_input = function (input) {
    var val = input.val().trim();
    if(val === '')
        input.parents('.form-group').removeClass('full');
    else
        input.parents('.form-group').addClass('full');

    if(input.attr('readonly'))
        input.parents('.form-group').addClass('readonly');
    else
        input.parents('.form-group').removeClass('readonly');

    if(input.attr('disabled'))
        input.parents('.form-group').addClass('disabled');
    else
        input.parents('.form-group').removeClass('disabled');
};

var set_slide = function () {
   $('.owl-carousel-slide').each(function () {
        var el = $(this);
        el.removeClass('owl-carousel-slide');
        el.owlCarousel({
            loop:true,
            margin:0,
            nav:false,
            dots:true,
            items:1
        });
   });
   $('.owl-carousel-activity').each(function () {
        var el = $(this);
        el.removeClass('owl-carousel-activity');
        el.owlCarousel({
            loop:true,
            margin:13,
            nav:false,
            dots:true,
            responsive : {
                0 : {
                    items : 1
                },
                550 : {
                   items : 2
                },
                1000 : {
                   items : 3
                },
                1200 : {
                    items : 4
                }
            }
        });
   });
   set_weigth();
};
var set_weigth = function () {
    var set_size = function (class_name, width_main, height_main) {
        var list = $('.' + class_name);
        for (var i = 0; i < list.length; i++) {
            if(list.eq(i).parents('[role="tabpanel"]').length > 0)
                if(!list.eq(i).parents('[role="tabpanel"]').hasClass('active')) continue;
            var width = list.eq(i).outerWidth();
            if (width > 0) {
                list.css('height', ((width * height_main) / width_main) + 'px');
                break;
            }
        }
    };
    set_size('set_slide',585,330);
    set_size('set_activity',276,153);
    set_size('set_shop_banner',262.5,147.1);
    set_size('set_shop_banner_big',541,147.1);
};
var set_select = function () {

    $('select[data-selected]').each(function(){
        var val = $(this).data('selected');
        $('option[value="'+val+'"]',this).attr('selected','selected').prop('selected',true);
    });

    $('input[data-check]').each(function(){
        var val = $(this).data('check');
        if($(this).val() == val) $(this).prop('checked',true);
    });

    $('select.select_wait').each(function(){
        $(this).selectpicker();
        $(this).removeClass('select_wait');
        $(this).addClass('select_set');
    });

    $('select.select_set').each(function(){
        $(this).selectpicker('refresh');
    });
};
var set_ranger = function () {
    var i = 0;
  $('.slider-input').each(function () {
      var el = $(this);
      var from = parseInt(el.attr('from'));
      var to = parseInt(el.attr('to'));
      var single = el.attr('type') === 'single';
      var name = el.attr('name');

      var id = "range_input_" + i;
      el.append('<div id="'+id+'" ></div>');
      el.append('<div class="range-detail" >')
      if(!single)
      {
          el.append('<span class="range-detail-start"></span>');
          el.append('<span class="range-detail-end"></span>');
      }
      el.append('<input class="hide" name="'+name+'" >');
      el.append('</div>');

      var input = $('input', el);
      input.val(single ? (to - from) / 2 : from + ',' + to);

      var item = document.getElementById(id);
      noUiSlider.create(item, {
          start: single ? (to - from) / 2 : [from, to],
          connect: single ? [true, false] : true,
          range: {
              'min': from,
              'max': to
          }
      });
      if(!single)
      {
          var start = el.find('.range-detail-start');
          var end = el.find('.range-detail-end');
          start.html(from);
          start.html(to);
      }

      item.noUiSlider.on('update', function( values, handle ) {
          if(!single)
          {
              start.html(getArabicNumbers(parseInt(values[0])));
              end.html(getArabicNumbers(parseInt(values[1])));
          }
          input.val(single ? values[0] : values[0] + ',' + values[1]);
      });
      i++;
  })
};
var set_tab = function () {
   $('.nav-tabs').each(function () {
        var list = $('li', this);
        list.css('width', (100 / list.length) + '%');
   });
};


/////////////////////////////////////////////////////////// function
var number_persian={0:'۰',1:'۱',2:'۲',3:'۳',4:'۴',5:'۵',6:'۶',7:'۷',8:'۸',9:'۹'};
function getArabicNumbers(str) {
    str = str + "";
    var new_str = "";
    for(var i = 0; i < str.length; i++)
    {
        new_str += isNumeric(str[i]) ? number_persian[str[i]] : str[i];
    }
    return new_str;
}
function isNumeric(value) {
    value = value + "";
    if(value[0] == '.') return false;
    value = value.replace('.','');
    if(value.indexOf('.') > -1) return false;
    return /^\d+$/.test(value);
}
function isTouchDevice() {
    return 'ontouchstart' in window        // works on most browsers
        || navigator.maxTouchPoints;       // works on IE10/11 and Surface
};
function isMobile() {
    var isMobile = false;
    if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent)
        || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) isMobile = true;
    return isMobile;
}