var datetime = {
    info:{
        year:0,
        month:0,
        day:0,
        months:[],
        monthsPersian:[],
        days:[],
        element:0,
        noOld:false,
        noNew:false,
        choose:{},
        metaDate:{
            set:false,
            year:0,
            month:0,
            day:0
        }
    },
    getNow:function(){

        var list = [];
        var year = 0;
        var month = 0;
        var day = 0;

        if(datetime.info.metaDate.set)
        {
            year = datetime.info.metaDate.year;
            day = datetime.info.metaDate.day;
            month = datetime.info.metaDate.month;
        }
        else{
            var listdate = new Date().toString().split(' ');
            year = parseInt(listdate[3]);
            day = parseInt(listdate[2]);
            month = datetime.info.months[listdate[1].toLowerCase()];
        }

        return {
            year : year,
            month : month,
            day : day,
            persian : JalaliDate.gregorianToJalali(year,month,day)
        }
    },
    init:function(){

        var meta = $('meta[name="datenow"]');
        if(meta.length > 0)
        {
            datetime.info.metaDate.set = true;
            var value = meta.attr('content').split('-');
            datetime.info.metaDate.day = parseInt(value[0]);
            datetime.info.metaDate.month = parseInt(value[1]);
            datetime.info.metaDate.year = parseInt(value[2]);
        }

        $(window).bind('resize',function(){
            datetime.remove();
        });

        datetime.info.months = {};
        datetime.info.months['jan'] = 1;
        datetime.info.months['feb'] = 2;
        datetime.info.months['mar'] = 3;
        datetime.info.months['apr'] = 4;
        datetime.info.months['may'] = 5;
        datetime.info.months['jun'] = 6;
        datetime.info.months['jul'] = 7;
        datetime.info.months['aug'] = 8;
        datetime.info.months['sep'] = 9;
        datetime.info.months['oct'] = 10;
        datetime.info.months['nov'] = 11;
        datetime.info.months['dec'] = 12;

        datetime.info.days = {};
        datetime.info.days['sat'] = 1;
        datetime.info.days['sun'] = 2;
        datetime.info.days['mon'] = 3;
        datetime.info.days['tue'] = 4;
        datetime.info.days['wed'] = 5;
        datetime.info.days['thu'] = 6;
        datetime.info.days['fri'] = 7;

        datetime.info.monthsPersian = [
            'فروردین',
            'اردیبهشت',
            'خرداد',
            'تیر',
            'مرداد',
            'شهریور',
            'مهر',
            'آبان',
            'آذر',
            'دی',
            'بهمن',
            'اسفند'
        ];

        var datenow = datetime.getNow();
        var year = datenow.year;
        var day = datenow.day;
        var month = datenow.month;

        var persinDate = datenow.persian;

        var id = 1;
        $('input.datepicker_ps').attr('readonly','readonly').each(function(){
            $(this).attr('data-picker',id).addClass('datepicker_ps_set');

            if($(this).data('default') && $(this).data('default') != '')
            {
                persinDate = $(this).data('default').split('/');
                for(var i in persinDate)
                    persinDate[i] = parseInt(persinDate[i]);

                datetime.info.choose[id] = [persinDate[0],persinDate[1],persinDate[2]];

                var strucrue = "yy/mm/dd";
                if($(this).data('strucrue') != undefined && $(this).data('strucrue') != "")
                {
                    strucrue = $(this).data('strucrue');
                }

                day = (persinDate[2] > 9)? persinDate[2] : "0" + persinDate[2];

                month = (persinDate[1] > 9)?
                    persinDate[1] : "0" + persinDate[1];

                strucrue = strucrue.replace('yy',persinDate[0]);
                strucrue = strucrue.replace('mm',month);
                strucrue = strucrue.replace('dd',day);

                $(this).val(strucrue);
            }
            else{
                datetime.info.choose[id] = [];
            }

            id++;
        });;
    },
    show:function(element){

        if(element.data('picker') == datetime.info.element) return;

        if($('.ps_picker').length < 1)
        {
            var html = '';
            html += '<div class="ps_picker">';
            html += '<div class="title">';
            html += '<a class="next ps_picker_year" data-year="-2"  href=""><i class="fa fa-chevron-up" ></i></a>';
            html += '<a class="next ps_picker_day" data-day="-2"  href=""><i class="fa fa-chevron-left" ></i></a>';
            // html += '<a class="next ps_picker_day" data-day="-2"  href="">&#62;</a>';
            html += '<a class="prev ps_picker_year" data-year="-1" href=""><i class="fa fa-chevron-down" ></i></a>';
            html += '<a class="prev ps_picker_day" data-day="-1" href=""><i class="fa fa-chevron-right" ></i></a>';
            // html += '<a class="prev ps_picker_day" data-day="-1" href="">&#60;</a>';
            html += '<span class="month_content"><span class="month"></span></span>';
            html += '<span class="year_content"><span class="year"></span><i class="year_up" ></i><i class="year_down" ></i></span>';
            html += '</div>';
            html += '<div class="list"><div class="head"><ul>';
            html += '<li>ش</li><li>ی</li><li>د</li><li>س</li><li>چ</li><li>پ</li><li>ج</li>';
            html += '</ul></div>';
            html += '<div class="days"><ul><li></li></ul></div></div>';
            html += '<div class="row row_control" >';
            html += '<div class="col-sm-6" ><a class="picker_today  btn btn-default btn-sm fit-width m-t-10" >امروز</a></div>';
            html += '<div class="col-sm-6" ><a class="picker_empty  btn btn-danger btn-sm fit-width m-t-10" >پاک کردن تاریخ</a></div>';
            html += '</div>';
            html += '</div>';
            $('body').append(html);
        }



        if(datetime.info.months.length == 0)
            datetime.init();

        datetime.info.noOld = element.data('disold') == true;
        datetime.info.noNew = element.data('disnew') == true;

        var widthBody = document.body.clientWidth;
        var heightBody = document.body.clientHeight;
        var topBody = $(window).scrollTop();
        var top = element.offset().top + element.outerHeight() + 10;
        var left = element.offset().left;
        var right = widthBody - (left + element.outerWidth());

        // check top and right
        var topToTop = top - topBody ;
        var topToBottom = heightBody - topToTop;

        if(topToBottom < 300 && topToBottom < topToTop)
        {
            top = element.offset().top - 300;
        }

        if(top < 0) top = 3;


        var rightToLeft = widthBody - right;
        var leftToRight = widthBody - left;

        if(rightToLeft < 250 && leftToRight > rightToLeft)
            right = widthBody - (left + 250);

        if(right + 250 > widthBody)
            right = widthBody - 250;

        if(right < 0) right = 3;

        var width = element.outerWidth();
        if(width < 250) width = 250;

        $('.ps_picker').css({'top':top + 'px','right':right + 'px','width': width+ 'px'});


        datetime.info.element = element.data('picker');

        if(datetime.info.choose[datetime.info.element].length > 0)
        {
            var data = datetime.info.choose[datetime.info.element];
            datetime.info.year = data[0];
            datetime.info.month = data[1];
            datetime.info.day = data[2];

            datetime.month(0);
        }
        else{
            var val = element.val();
            if(val == '')
            {
                var datenow = datetime.getNow();
                var year = datenow.year;
                var day = datenow.day;
                month = datenow.month;

                var persinDate = datenow.persian;

                if(element.data('oldyear') != undefined)
                {
                    persinDate[0] -= parseInt(element.data('oldyear'));
                    datetime.info.year = persinDate[0];
                    datetime.info.month =1;
                    datetime.info.day = 1;
                }
                else{
                    datetime.info.year = persinDate[0];
                    datetime.info.month = persinDate[1];
                    datetime.info.day = persinDate[2];
                }
            }
            else{
                val = val.split('/');
                datetime.info.year = val[0];
                datetime.info.month = val[1];
                datetime.info.day = val[2];
            }
            datetime.month(0);
        }
    },
    choose:function(day)
    {
        var id = datetime.info.element;
        datetime.remove();
        datetime.info.choose[id] = [datetime.info.year,datetime.info.month,day];
        var element = $('.datepicker_ps[data-picker="'+id+'"]');

        var strucrue = "yy/mm/dd";
        if(element.data('strucrue') != undefined && element.data('strucrue') != "")
        {
            strucrue = element.data('strucrue');
        }

        day = (day > 9)? day : "0" + day;

        var month = (datetime.info.month > 9)?
            datetime.info.month : "0" + datetime.info.month;

        strucrue = strucrue.replace('yy',datetime.info.year);
        strucrue = strucrue.replace('mm',month);
        strucrue = strucrue.replace('dd',day);

        element.val(strucrue);
        element.trigger('change');
        element.trigger('keydown');
        element.trigger('keyup');
    },
    choose_today : function () {
        var date_now = datetime.getNow().persian;
        datetime.info.year = date_now[0];
        datetime.info.month = date_now[1];
        datetime.choose(date_now[2]);
    },
    clean:function(){
        var id = datetime.info.element;
        datetime.remove();
        datetime.info.choose[id] = [];
        var element = $('.datepicker_ps[data-picker="'+id+'"]');
        element.val('');
        element.trigger('change');
        element.trigger('keydown');
        element.trigger('keyup');
    },
    month:function(number){
        if(number != 0)
        {
            var month = datetime.info.month;
            var year = datetime.info.year;

            if(number == -1)
            {
                month = month -1;
                if(month == 0) {
                    month = 12;
                    year = year - 1;
                }
            }
            else{
                month = month + 1;
                if(month == 13) {
                    month = 1;
                    year = year + 1;
                }
            }

            datetime.info.month = month;
            datetime.info.year = year;
        }

        // get now info
        var nowTime = {
            month : -1,
            year : -1,
            day : -1
        };

        if(datetime.info.noOld || datetime.info.noNew)
        {
            var datenow = datetime.getNow();

            nowTime.year = datenow.year;
            nowTime.day = datenow.day;
            nowTime.month = datenow.month;
            var persinDateNow = datenow.persian;

            nowTime.year = persinDateNow[0];
            nowTime.month = persinDateNow[1];
            nowTime.day = persinDateNow[2];
        }

        var object = $('.ps_picker');

        if(datetime.info.noOld)
        {
            if(datetime.info.month == nowTime.month && datetime.info.year >= nowTime.year)
                $('.ps_picker_day.prev',object).addClass('disabled');
            else
                $('.ps_picker_day.prev',object).removeClass('disabled');

            if(datetime.info.year <= nowTime.year)
                $('.ps_picker_year.prev',object).addClass('disabled');
            else
                $('.ps_picker_year.prev',object).removeClass('disabled');
        }

        if(datetime.info.noNew)
        {
            if(datetime.info.month == nowTime.month && datetime.info.year >= nowTime.year)
                $('.ps_picker_day.next',object).addClass('disabled');
            else
                $('.ps_picker_day.next',object).removeClass('disabled');

            if(datetime.info.year >= nowTime.year)
                $('.ps_picker_year.next',object).addClass('disabled');
            else
                $('.ps_picker_year.next',object).removeClass('disabled');
        }

        $('.month',object).html(datetime.info.monthsPersian[datetime.info.month - 1]);
        $('.year',object).html(datetime.info.year);

        var day = (datetime.info.month > 6)? 30 : 31;
        if(datetime.info.month == 12 && !Cabise(datetime.info.year)) day = 29;

        $('.list .days ul',object).html('');

        var listMiladi = JalaliDate.jalaliToGregorian(datetime.info.year,datetime.info.month,1);

        var d = new Date(listMiladi[0],listMiladi[1]-1,listMiladi[2]);

        var dayStart = d.getDay() + 1;
        if(dayStart > 6) dayStart = 0;

        for(var i = 1 ; i <= dayStart; i++)
        {
            $('.list .days ul',object).append('<li></li>');
        }
        for(var i = 1 ; i <= day; i++)
        {
            var className = "ps_picker_day";

            if(datetime.info.month == nowTime.month
                && datetime.info.year == nowTime.year
                && datetime.info.noOld && i < nowTime.day
            )
            {
                className = "";
            }

            if(datetime.info.month == nowTime.month
                && datetime.info.year == nowTime.year
                && datetime.info.noNew && i > nowTime.day
            )
            {
                className = "";
            }

            $('.list .days ul',object).append('<li><a class="'+className+'" data-day="'+i+'" >'+i+'</a></li>');
        }

        if(datetime.info.day > day) datetime.info.day = 1;

        $('.list .days ul a[data-day="'+datetime.info.day+'"]',object).addClass('active');
    },
    year : function (year_new) {
        var year = datetime.info.year;
        if(year_new == -2)
            year++;
        else
            year--;
        datetime.info.year = year;
        datetime.info.day = 1;
        this.month(0);
    },
    remove:function(){
        datetime.info.element = 0;
        $('.ps_picker').remove();
    }
};
var get_timestamp_datetime = function (text) {
    if(text.indexOf('/') > -1) return text;
    if(text == '0000-00-00 00:00:00') return '';
    text = text.split(' ')[0].split('-');
    text = gregorian_to_jalali(parseInt(text[0]),parseInt(text[1]),parseInt(text[2]));
    if(text[1] < 10) text[1] = '0' + text[1];
    if(text[2] < 10) text[2] = '0' + text[2];
    return text[0] + "/" + text[1] + "/" + text[2];
};

var checkPicker = true;
$(document).on('click','.datepicker_ps_set:not(:disabled)',function(e){
    e.preventDefault();
    datetime_show($(this));
});

var datetime_show = function (element) {
    datetime.show(element);
    checkPicker = false;
};

$(document).on('click','.picker_empty',function(e){
    e.preventDefault();
    datetime.clean();
    checkPicker = false;
});

$(document).on('click','.picker_today',function(e){
    e.preventDefault();
    datetime.choose_today();
});

$(document).on('click','.ps_picker_day:not(.disabled)',function(e){
    e.preventDefault();
    if($(this).hasClass('disabled')) return false;
    var day = parseInt($(this).data('day'));
    if(day > 0)
        datetime.choose(day);
    else
        datetime.month(day);
    return true;
});

$(document).on('click','.ps_picker_year:not(.disabled)',function(e){
    e.preventDefault();
    if($(this).hasClass('disabled')) return false;
    var year = parseInt($(this).data('year'));
    datetime.year(year);
    return true;
});

$(document).on('click','.ps_picker',function(e){
    e.preventDefault();
    checkPicker = false;
});

$(document).on('click',function(e){
    if(checkPicker) datetime.remove();
    checkPicker = true;
});

function Cabise(year)
{
    var a = 0.025;
    var b = 266;
    var leapDays0 = 0;
    var leapDays1  = 0;
    if(year > 0)
    {
        leapDays0 = ((year + 38) % 2820)*0.24219 + a ; // 0.24219 ~ extra days of one year
        leapDays1 = ((year + 39) % 2820)*0.24219 + a ; // 38 days is the difference of epoch to 2820-year cycle
    }
    else{
        if(year < 0)
        {
            leapDays0 = ((year + 39) % 2820)*0.24219 + a
            leapDays1 = ((year + 40) % 2820)*0.24219 + a
        }
        else{
            return false;
        }
    }

    var frac0 = parseInt((leapDays0 - parseInt(leapDays0))*1000);
    var frac1 = parseInt((leapDays1 - parseInt(leapDays1))*1000);

    return (frac0 <= b && frac1 > b)
}

JalaliDate = {
    g_days_in_month: [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
    j_days_in_month: [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
};

JalaliDate.jalaliToGregorian = function(j_y, j_m, j_d)
{
    j_y = parseInt(j_y);
    j_m = parseInt(j_m);
    j_d = parseInt(j_d);
    var jy = j_y-979;
    var jm = j_m-1;
    var jd = j_d-1;

    var j_day_no = 365*jy + parseInt(jy / 33)*8 + parseInt((jy%33+3) / 4);
    for (var i=0; i < jm; ++i) j_day_no += JalaliDate.j_days_in_month[i];

    j_day_no += jd;

    var g_day_no = j_day_no+79;

    var gy = 1600 + 400 * parseInt(g_day_no / 146097); /* 146097 = 365*400 + 400/4 - 400/100 + 400/400 */
    g_day_no = g_day_no % 146097;

    var leap = true;
    if (g_day_no >= 36525) /* 36525 = 365*100 + 100/4 */
    {
        g_day_no--;
        gy += 100*parseInt(g_day_no/  36524); /* 36524 = 365*100 + 100/4 - 100/100 */
        g_day_no = g_day_no % 36524;

        if (g_day_no >= 365)
            g_day_no++;
        else
            leap = false;
    }

    gy += 4*parseInt(g_day_no/ 1461); /* 1461 = 365*4 + 4/4 */
    g_day_no %= 1461;

    if (g_day_no >= 366) {
        leap = false;

        g_day_no--;
        gy += parseInt(g_day_no/ 365);
        g_day_no = g_day_no % 365;
    }

    for (var i = 0; g_day_no >= JalaliDate.g_days_in_month[i] + (i == 1 && leap); i++)
        g_day_no -= JalaliDate.g_days_in_month[i] + (i == 1 && leap);
    var gm = i+1;
    var gd = g_day_no+1;

    return [gy, gm, gd];
}

JalaliDate.gregorianToJalali = function(g_y, g_m, g_d)
{
    g_y = parseInt(g_y);
    g_m = parseInt(g_m);
    g_d = parseInt(g_d);
    var gy = g_y-1600;
    var gm = g_m-1;
    var gd = g_d-1;

    var g_day_no = 365*gy+parseInt((gy+3) / 4)-parseInt((gy+99)/100)+parseInt((gy+399)/400);

    for (var i=0; i < gm; ++i)
        g_day_no += JalaliDate.g_days_in_month[i];
    if (gm>1 && ((gy%4==0 && gy%100!=0) || (gy%400==0)))
    /* leap and after Feb */
        ++g_day_no;
    g_day_no += gd;

    var j_day_no = g_day_no-79;

    var j_np = parseInt(j_day_no/ 12053);
    j_day_no %= 12053;

    var jy = 979+33*j_np+4*parseInt(j_day_no/1461);

    j_day_no %= 1461;

    if (j_day_no >= 366) {
        jy += parseInt((j_day_no-1)/ 365);
        j_day_no = (j_day_no-1)%365;
    }

    for (var i = 0; i < 11 && j_day_no >= JalaliDate.j_days_in_month[i]; ++i) {
        j_day_no -= JalaliDate.j_days_in_month[i];
    }
    var jm = i+1;
    var jd = j_day_no+1;


    return [jy, jm, jd];
}


JalaliDate.jalaliToGregorian = function(j_y, j_m, j_d)
{
    j_y = parseInt(j_y);
    j_m = parseInt(j_m);
    j_d = parseInt(j_d);
    var jy = j_y-979;
    var jm = j_m-1;
    var jd = j_d-1;

    var j_day_no = 365*jy + parseInt(jy / 33)*8 + parseInt((jy%33+3) / 4);
    for (var i=0; i < jm; ++i) j_day_no += JalaliDate.j_days_in_month[i];

    j_day_no += jd;

    var g_day_no = j_day_no+79;

    var gy = 1600 + 400 * parseInt(g_day_no / 146097); /* 146097 = 365*400 + 400/4 - 400/100 + 400/400 */
    g_day_no = g_day_no % 146097;

    var leap = true;
    if (g_day_no >= 36525) /* 36525 = 365*100 + 100/4 */
    {
        g_day_no--;
        gy += 100*parseInt(g_day_no/  36524); /* 36524 = 365*100 + 100/4 - 100/100 */
        g_day_no = g_day_no % 36524;

        if (g_day_no >= 365)
            g_day_no++;
        else
            leap = false;
    }

    gy += 4*parseInt(g_day_no/ 1461); /* 1461 = 365*4 + 4/4 */
    g_day_no %= 1461;

    if (g_day_no >= 366) {
        leap = false;

        g_day_no--;
        gy += parseInt(g_day_no/ 365);
        g_day_no = g_day_no % 365;
    }

    for (var i = 0; g_day_no >= JalaliDate.g_days_in_month[i] + (i == 1 && leap); i++)
        g_day_no -= JalaliDate.g_days_in_month[i] + (i == 1 && leap);
    var gm = i+1;
    var gd = g_day_no+1;

    return [gy, gm, gd];
};

datetime.init();