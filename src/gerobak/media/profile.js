(function() {

function create_show_package_link(pkg) {
    return '<a href="show/'+pkg+'/" onclick="profile.show(\''+pkg+'\'); return false;">'+pkg+'</a>';
}

var ph = {
    install: {
        packages: [],

        _add: function(pkgs) {
            var items = pkgs.split(" ");
            var len = items.length;
            for (var i=0; i<len; i++) {
                var item = items[i];
                if ((item.length > 0) && (this.packages.indexOf(item) == -1)) {
                    this.packages.push(item);
                }
            }
        },

        _remove: function(pkg) {
            var pos = this.packages.indexOf(pkg);
            if (pos >= 0) {
                this.packages.splice(pos, 1);
            }
        },

        _clear: function() {
            this.packages = [];
        },

        update_list: function() {
            var obj = $('#install-package-list ul');
            var html = '';
            var len = this.packages.length;
            for (var i=0; i<len; i++) {
                var pkg = this.packages[i];
                html += '<li>'+create_show_package_link(pkg);
                html += '<sup onclick="profile.install.remove(\''+pkg+'\')">x</sup></li> ';
            }
            obj.html(html);
            if (len > 0) {
                $('#install-package-button').show();
                $('#install-package-list').show();
            }
            else {
                $('#install-package-button').hide();
                $('#install-package-list').hide();
            }
        },

        add_form: function() {
            var pkgs = $('#install-package-add')[0].value;
            this.add(pkgs);
            $('#install-package-add').select();
        },

        add: function(pkgs) {
            this._add(pkgs);
            this.update_list();
        },

        remove: function(pkg) {
            this._remove(pkg);
            this.update_list();
        },

        clear: function() {
            this._clear();
            this.update_list();
            $('#install-package-add').select();
        },

        _create_package_list: function(items, title) {
            if (items == undefined) { return ''; }
            var len = items.length;
            if (len == 0) { return ''; }
        
            var html = '';
            html += '<div class="pkgs"><h3>'+title+'</h3>';
            
            var list = [];
            for (var i=0; i<len; i++) {
                list.push(create_show_package_link(items[i]));
            }

            html += '<p>' + list.join(', ') + '</p>';
        
            html += '</div>';
            return html;
        },

        show: function(data, target) {
            if (target == undefined) {
                target = '#install-result';
            }
        
            var obj = $(target);
            var type = data.type;
            var data = data.data;
            var html = '';

            obj.html('<div class="install-result"></div>');
            obj = obj.find('.install-result');

            var pkgs = data.packages.join(' ');

            if (type == 'install') {
                html += '<p>Installation result for <strong>'+pkgs+'</strong>:</p>';
            }
            else if (type == "upgrade") {
                html += '<p>Result of <strong>upgrade</strong> operation:</p>';
            }
            else if (type == "dist-upgrade") {
                html += '<p>Result of <strong>dist-upgrade</strong> operation:</p>';
            }
        
            if (data.errors.length > 0) {
                html += '<div class="error"><p><span>Unable to install.</span> Error messages:</p></ul>';
                var len = data.errors.length;
                for (var i=0; i<len; i++) {
                    html += '<li>'+data.errors[i]+'</li>';
                }
                html += '</ul></div>';
                obj.html(html);
            }
            else {
                html += '<div class="head"></div><div class="side"></div><div class="main"></div>';
                obj.html(html);

                var head = obj.find('.head');
                var side = obj.find('.side');
                var main = obj.find('.main');

                // Already the newest version
                if (data.newest.length > 0) {
                    var items = [];
                    var len = data.newest.length;
                    for (var i=0; i<len; i++) {
                        items.push(create_show_package_link(data.newest[i]));
                    }
                    html = '<p>Already the newest version: ' + items.join(', ') + '</p>';
                    head.html(html);
                }

                // URL list
                if (data.urls.length > 0) {
                    html = '';
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
                        html += '<li><a href="'+url+'">'+url+'</a></li>';
                    }
        
                    html += '</ul>';
                    main.html(html);
                }
        
                // install
        
                html = '';
                html += this._create_package_list(data.install, 'To Be Installed');
                html += this._create_package_list(data.upgrade, 'To Be Upgraded');
                html += this._create_package_list(data.recommended, 'Recommended');
                html += this._create_package_list(data.suggested, 'Suggested');
        
                side.html(html);
            }

            obj.show();
        },

        start: function() {
            var packages = this.packages.join(" ");
            var self = this;
            $.ajax({
                type: 'POST',
                url: 'install/?format=json',
                dataType: 'json',
                data: {packages: packages},
                complete: function(xhr, stat) {
                    console.log('complete.', 'stat:', stat);
                },
                success: function(data, stat) {
                    self.show(data);
                }
            });
        }
    },

    show: function(pkg) {
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
    },

    search: {
    
        show: function(query, data) {
            var items = data.data.items;
            var len = items.length;
            var obj = $('#search-result');

            if (len == 0) {
                var html = '';
                html += '<p>No package found. Please try another keyword.</p>';
                obj.html(html);
            }
            else {
                var html = '';
                html += '<p>Search result for <strong>'+query+'</strong>:</p>';
                html += '<table class="search"></table>';
                obj.html(html);
                var table = obj.find('table');
                table.append('<tr><th></th><th>Package</th><th>Description</th><th></th></tr>');
                for (var i=0; i<len; i++) {
                    var pkg = items[i][0];
                    var desc = items[i][1];
                    var pkglink = create_show_package_link(pkg);
                    var addlink = '';
                    if (ph.install.packages.indexOf(pkg) == -1) {
                        addlink = '<span onclick="profile.search.add(this, \''+pkg+'\')">add</span>';
                    }
                    else {
                        addlink = '<span>added</span>';
                    }
                    table.append('<tr><td>'+(i+1)+'</td><td>'+pkglink+'</td><td>'+desc+'</td><td>'+addlink+'</td></tr>');
                }
            }
            obj.show();
        },

        add: function(src, pkg) {
            ph.install.add(pkg);
            $(src).parent().html('<span>added</span>');
        },

        start: function(f) {
            var query = f.packages.value;
            var self = this;
            $.ajax({
                type: 'POST',
                url: 'search/?format=json',
                dataType: 'json',
                data: {packages: query},
                complete: function(xhr, stat) {
                    console.log('complete');
                    console.log('stat:', stat);
                },
                success: function(data, stat) {
                    self.show(query, data);
                }
            });
        }
    },

    dist_upgrade: {
        start: function() {
            ph.upgrade._start('dist-upgrade');
        }
    },

    upgrade: {
        start: function() {
            this._start('upgrade');
        },

        _start: function(path) {
            $.ajax({
                type: 'POST',
                url: path + '/?format=json',
                dataType: 'json',
                complete: function(xhr, stat) {
                    console.log('complete.', 'stat:', stat);
                },
                success: function(data, stat) {
                    ph.install.show(data, '#upgrade-result');
                }
            });
        }
    },

    init: function() {
        this._init_dialogs();
        this._init_tabs();
    },

    _init_dialogs: function() {
        $('.dialog').dialog({autoOpen: false, modal: true});
        $('#dialog-status-upload').dialog('option', 'width', 500);
        $('#dialog-sources').dialog('option', 'width', 500);
        $('#dialog-package-show').dialog('option', 'width', 700);
        $('#dialog-package-show').dialog('option', 'maxHeight', 500);
    },

    _init_tabs: function() {
        $('.tabs').tabs();
    }
}

this.profile = ph;
})();

function show_dialog(s) {
    $(s).dialog('open');
}   
function htmlentities(txt) {
    txt = txt.replace(/</g, '&lt;');
    txt = txt.replace(/>/g, '&gt;');
    return txt;
}
