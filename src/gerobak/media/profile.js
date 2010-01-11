var install_package_list = [];
function init_install_tab() {
    $('#install form').hide();

    var html = '';
    html += '<form onsubmit="install_package_add_form(); return false;">';
    html += '<p><label>Package:</label> <input type="text" id="install-package-add"/> ';
    html += '<input type="submit" value="add"/> ';
    html += '<input type="button" value="clear" onclick="install_package_clear()"/></p>';
    html += '</form>';
    html += '<ul id="install-package-list"></ul>';
    html += '<div id="install-package-button"><input type="button" value="install" onclick="install_packages()"/></div>';

    $('#install form').after(html);
}

function install_package_append(pkgs) {
    var items = pkgs.split(" ");
    var len = items.length;
    for (var i=0; i<len; i++) {
        var item = items[i];
        if ((item.length > 0) && (install_package_list.indexOf(item) == -1)) {
            install_package_list.push(item);
        }
    }
}
function install_update_list() {
    var obj = $('#install-package-list');
    var html = '';
    var len = install_package_list.length;
    for (var i=0; i<len; i++) {
        var pkg = install_package_list[i];
        html += '<li><span onclick="show_package(\''+pkg+'\')">'+pkg+'</span>';
        html += '<sup onclick="install_package_remove(\''+pkg+'\')">x</sup></li> ';
    }
    obj.html(html);
    if (len > 0) {
        $('#install-package-button').show();
    }
    else {
        $('#install-package-button').hide();
    }
}
function install_package_add_form() {
    var pkgs = $('#install-package-add')[0].value;
    install_package_add(pkgs);
    $('#install-package-add').select();
}
function install_package_add(pkgs) {
    install_package_append(pkgs);
    install_update_list();
}
function install_package_remove(pkg) {
    var pos = install_package_list.indexOf(pkg);
    if (pos >= 0) {
        install_package_list.splice(pos, 1);
    }
    install_update_list();
}
function install_package_clear() {
    install_package_list = [];
    install_update_list();
    $('#install-package-add').select();
}
function install_packages() {
    var packages = install_package_list.join(" ");
    $.ajax({
        type: 'POST',
        url: 'install/?format=json',
        dataType: 'json',
        data: {packages: packages},
        complete: function(xhr, stat) {
            console.log('complete.', 'stat:', stat);
        },
        success: function(data, stat) {
            show_install(data);
        }
    });
}

function show_install(data, target) {
    if (target == undefined) {
        target = '#install-result';
    }

    var data = data.data;
    var obj = $(target);
    obj.html('<div class="install-result"><div class="side"></div><div class="main"></div></div>');

    var side = obj.find('.side');
    var main = obj.find('.main');

    var html = '';

    // URL list
    html += '<h3>URLs</h3>';
    html += '<ul>';

    var len = data.urls.length;
    for (var i=0; i<len; i++) {
        var item = data.urls[i];
        var url = item[0];
        var deb = item[1];
        var size = item[2];
        var hash = item[3];
        var hash_format = item[4];
        html += '<li>'+i+' <a href="'+url+'">'+url+'</a></li>';
    }

    html += '</ul>';
    main.html(html);

    // install

    html = '';
    html += create_package_list(data.install, 'To Be Installed');
    html += create_package_list(data.upgrade, 'To Be Upgraded');
    html += create_package_list(data.recommended, 'Recommended');
    html += create_package_list(data.suggested, 'Suggested');

    side.html(html);

}

function create_package_list(items, title) {
    if (items == undefined) { return ''; }
    var len = items.length;
    if (len == 0) { return ''; }

    var html = '';
    html += '<div class="pkgs"><h3>'+title+'</h3>';
    
    html += '<p><span onclick="show_package(\''+items[0]+'\')">'+items[0]+'</span>';
    for (var i=1; i<len; i++) {
        html += ', <span onclick="show_package(\''+items[i]+'\')">'+items[i]+'</span>';
    }
    html += '</p>';

    html += '</div>';
    return html;
}

$(document).ready(function() {
    $('.dialog').dialog({autoOpen: false, modal: true});
    $('#dialog-status-upload').dialog('option', 'width', 500);
    $('#dialog-sources').dialog('option', 'width', 500);
    $('#dialog-package-show').dialog('option', 'width', 700);
    $('#dialog-package-show').dialog('option', 'maxHeight', 500);
    $('.tabs').tabs();
    init_install_tab();
});
function show_dialog(s) {
    $(s).dialog('open');
}   
function htmlentities(txt) {
    txt = txt.replace(/</g, '&lt;');
    txt = txt.replace(/>/g, '&gt;');
    return txt;
}
function show_package(pkg) {
    console.log('show package:', pkg);
    var dialog = $('#dialog-package-show');
    dialog.find('h3').text(pkg);
    dialog.find('div').text('');
    dialog.find('p').text('');
    dialog.find('pre').html('');
    dialog.find('table').html('');
    dialog.dialog('open');
    $.getJSON('show/'+pkg+'/?format=json', function(data, stat) {
        console.log('stat:', stat);
        dialog.find('p.desc').text(data.data.sdesc);
        dialog.find('pre.desc').text(data.data.desc);

        var table = dialog.find('table');
        var info = data.data.data;
        var len = info.length;
        for (var i=0; i<len; i++) {
            var key = info[i][0];
            var value = htmlentities(info[i][1]);
            if (key != 'Description') {
                table.append('<tr><td>'+key+'</td><td>'+value+'</td></tr>');
            }
        }
        dialog.dialog('option', 'position', ['center', 25]);
        dialog.dialog('option', 'title', data.data.package);
    });
    return false;
}
function show_search(data) {
    var items = data.data.items;
    var len = items.length;
    var obj = $('#search-result');
    obj.html('<table class="search"></table>');
    var table = obj.find('table');
    table.append('<tr><th></th><th>Package</th><th>Description</th><th></th></tr>');
    for (var i=0; i<len; i++) {
        var pkg = items[i][0];
        var desc = items[i][1];
        var pkglink = '<a href="show/'+pkg+'/" onclick="return show_package(\''+pkg+'\')">'+pkg+'</a>';
        var addlink = '';
        if (install_package_list.indexOf(pkg) == -1) {
            addlink = '<span onclick="search_package_add(this, \''+pkg+'\')">add</span>';
        }
        else {
            addlink = '<span>added</span>';
        }
        table.append('<tr><td>'+(i+1)+'</td><td>'+pkglink+'</td><td>'+desc+'</td><td>'+addlink+'</td></tr>');
    }
}
function search_package_add(src, pkg) {
    install_package_add(pkg);
    $(src).parent().html('<span>added</span>');
}
function submit_dist_upgrade() {
    return submit_upgrade('dist-upgrade');
}
function submit_upgrade(path) {
    if (path == undefined) {
        path = 'upgrade';
    }
    $.ajax({
        type: 'POST',
        url: path + '/?format=json',
        dataType: 'json',
        complete: function(xhr, stat) {
            console.log('complete.', 'stat:', stat);
        },
        success: function(data, stat) {
            show_install(data, '#upgrade-result');
        }
    });
    return false;
}
function submit_search(f) {
    var packages = f.packages.value;
    $.ajax({
        type: 'POST',
        url: 'search/?format=json',
        dataType: 'json',
        data: {packages: packages},
        complete: function(xhr, stat) {
            console.log('complete');
            console.log('stat:', stat);
        },
        success: function(data, stat) {
            show_search(data);
        }
    });
    return false;
}