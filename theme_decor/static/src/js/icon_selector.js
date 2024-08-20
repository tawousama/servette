/** @odoo-module */

var { MediaDialog } = require("@web_editor/components/media_dialog/media_dialog");
var { patch } = require("web.utils");
var { ImageSelector } = require('@web_editor/components/media_dialog/image_selector');
var { DocumentSelector } = require('@web_editor/components/media_dialog/document_selector');
var { IconSelector } = require('@web_editor/components/media_dialog/icon_selector');
var { VideoSelector } = require('@web_editor/components/media_dialog/video_selector');

export const TABS = {
    IMAGES: {
        id: 'IMAGES',
        title: "Images",
        Component: ImageSelector,
    },
    DOCUMENTS: {
        id: 'DOCUMENTS',
        title: "Documents",
        Component: DocumentSelector,
    },
    ICONS: {
        id: 'ICONS',
        title: "Icons",
        Component: IconSelector,
    },
    VIDEOS: {
        id: 'VIDEOS',
        title: "Videos",
        Component: VideoSelector,
    },
};

patch(MediaDialog.prototype, "theme_decor.iconSelectorJS", {
    async save() {
        const selectedMedia = this.selectedMedia[this.state.activeTab];
        if (selectedMedia.length) {
            const elements = await TABS[this.state.activeTab].Component.createElements(selectedMedia, { rpc: this.rpc, orm: this.orm });
            elements.forEach(element => {
                if (this.props.media) {
                    element.classList.add(...this.props.media.classList);
                    const style = this.props.media.getAttribute('style');
                    if (style) {
                        element.setAttribute('style', style);
                    }
                    if (this.props.media.dataset.shape) {
                        element.dataset.shape = this.props.media.dataset.shape;
                    }
                    if (this.props.media.dataset.shapeColors) {
                        element.dataset.shapeColors = this.props.media.dataset.shapeColors;
                    }
                }
                for (const otherTab of Object.keys(TABS).filter(key => key !== this.state.activeTab)) {
                    for (const property of TABS[otherTab].Component.mediaSpecificStyles) {
                        element.style.removeProperty(property);
                    }
                    element.classList.remove(...TABS[otherTab].Component.mediaSpecificClasses);
                    const extraClassesToRemove = [];
                    for (const name of TABS[otherTab].Component.mediaExtraClasses) {
                        if (typeof(name) === 'string') {
                            extraClassesToRemove.push(name);
                        } else { // Regex
                            for (const className of element.classList) {
                                if (className.match(name)) {
                                    extraClassesToRemove.push(className);
                                }
                            }
                        }
                    }
                    // Remove classes that do not also exist in the target type.
                    element.classList.remove(...extraClassesToRemove.filter(candidateName => {
                        for (const name of TABS[this.state.activeTab].Component.mediaExtraClasses) {
                            if (typeof(name) === 'string') {
                                if (candidateName === name) {
                                    return false;
                                }
                            } else { // Regex
                                for (const className of element.classList) {
                                    if (className.match(candidateName)) {
                                        return false;
                                    }
                                }
                            }
                        }
                        return true;
                    }));
                }
                element.classList.remove(...this.initialIconClasses);
                element.classList.remove('o_modified_image_to_save');
                element.classList.remove('oe_edited_link');
                element.classList.add(...TABS[this.state.activeTab].Component.mediaSpecificClasses);
                if (this.state.activeTab == 'ICONS') {

                    var selectediconbase = selectedMedia[0].fontBase

                    if (selectediconbase == "lnr"){
                        element.classList.remove(...['icon', 'icofont', 'lni', 'ri', 'ti', 'fa'])
                    }
                    if (selectediconbase == "icon"){
                        element.classList.remove(...['lnr', 'icofont', 'lni', 'ri', 'ti', 'fa'])
                    }
                    if (selectediconbase == "icofont"){
                        element.classList.remove(...['lnr', 'icon', 'lni', 'ri', 'ti', 'fa'])
                    }
                    if (selectediconbase == "lni"){
                        element.classList.remove(...['lnr', 'icofont', 'icon', 'ri', 'ti', 'fa'])
                    }
                    if (selectediconbase == "ri"){
                        element.classList.remove(...['lnr', 'icofont', 'icon', 'lni', 'ti', 'fa'])
                    }
                    if (selectediconbase == "ti"){
                        element.classList.remove(...['lnr', 'icofont', 'icon', 'lni', 'ri', 'fa'])
                    }
                    if (selectediconbase == "fa"){
                        element.classList.remove(...['lnr', 'icofont', 'icon', 'lni', 'ri', 'ti'])
                    }
                }
            });
            if (this.props.multiImages) {
                this.props.save(elements);
            } else {
                this.props.save(elements[0]);
            }
        }
        this.props.close();
    }
});