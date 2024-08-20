odoo.define('theme_decor.ButtonStyle', function (require) {
'use strict';
	
	var core = require('web.core');
	const _DialogLinkWidget = require('wysiwyg.widgets.LinkDialog');
	const LinkTools = require('wysiwyg.widgets.LinkTools');
	const Link = require('wysiwyg.widgets.Link');
	var _t = core._t;

	const DecorLinkDialog = _DialogLinkWidget.include({
		_getLinkOptions: function () {
	        const options = [
	            'input[name="link_style_color"]',
	            'select[name="link_style_size"] > option',
	            'select[name="link_style_shape"] > option',
	            'select[name="link_hover_style"] > option',
	        ];
	        return this.$(options.join(','));
	    },

	    _getLinkStyle: function () {
	        return this.$('select[name="link_hover_style"]').val() || '';
	    },
	});

	const DecorLinkTools = LinkTools.include({
		xmlDependencies: (LinkTools.prototype.xmlDependencies || [])
        .concat([
            '/theme_decor/static/src/xml/button_editor.xml',
        ]),
		_getLinkOptions: function () {
	        const options = [
	            'we-selection-items[name="link_style_color"] > we-button',
	            'we-selection-items[name="link_style_size"] > we-button',
	            'we-selection-items[name="link_style_shape"] > we-button',
	            'we-selection-items[name="link_hover_style"] > we-button',
	        ];
	        return this.$(options.join(','));
	    },

	    _getLinkStyle: function () {
	        return this.$('we-selection-items[name="link_hover_style"] we-button.active').data('value') || '';
	    },
	});

	const DecorLink = Link.include({
		_getData: function () {
	        var $url = this.$('input[name="url"]');
	        var url = $url.val();
	        var content = this.$('input[name="label"]').val() || url;

	        if (!this.isButton && $url.prop('required') && (!url || !$url[0].checkValidity())) {
	            return null;
	        }

	        const type = this._getLinkType();
	        const customTextColor = this._getLinkCustomTextColor();
	        const customFill = this._getLinkCustomFill();
	        const customBorder = this._getLinkCustomBorder();
	        const customBorderWidth = this._getLinkCustomBorderWidth();
	        const customBorderStyle = this._getLinkCustomBorderStyle();
			const customClasses = this._getLinkCustomClasses();
	        const size = this._getLinkSize();
	        const shape = this._getLinkShape();
	        const hoverstyle = this._getLinkStyle();
	        const shapes = shape ? shape.split(',') : [];
	        const style = ['outline', 'fill'].includes(shapes[0]) ? `${shapes[0]}-` : '';
	        const shapeClasses = shapes.slice(style ? 1 : 0).join(' ');
	        const classes = (this.data.className || '') +
	            (type ? (` btn btn-${style}${type}`) : '') +
				(type === 'custom' ? customClasses : '') +
	            (type && shapeClasses ? (` ${shapeClasses}`) : '') +
	            (type && size ? (' btn-' + size) : '') + 
	            (type && hoverstyle ? (' btn-' + hoverstyle) : '');
	        var isNewWindow = this._isNewWindow(url);
	        var doStripDomain = this._doStripDomain();
	        if (url.indexOf('@') >= 0 && url.indexOf('mailto:') < 0 && !url.match(/^http[s]?/i)) {
	            url = ('mailto:' + url);
	        } else if (url.indexOf(location.origin) === 0 && doStripDomain) {
	            url = url.slice(location.origin.length);
	        }
	        var allWhitespace = /\s+/gi;
	        var allStartAndEndSpace = /^\s+|\s+$/gi;
	        return {
	            content: content,
	            url: this._correctLink(url),
	            classes: classes.replace(allWhitespace, ' ').replace(allStartAndEndSpace, ''),
	            customTextColor: customTextColor,
	            customFill: customFill,
	            customBorder: customBorder,
	            customBorderWidth: customBorderWidth,
	            customBorderStyle: customBorderStyle,
	            oldAttributes: this.data.oldAttributes,
	            isNewWindow: isNewWindow,
	            doStripDomain: doStripDomain,
	        };
	    },

	     _getLinkStyle: function () {},
	});


});