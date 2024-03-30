# For neo4j

### OUR Dataset
CREATE (n:Style { name: 'Color', level: 'High level' }) return n;
CREATE (n:Style { name: 'Typography', level: 'High level' }) return n;
CREATE (n:Style { name: 'Icon', level: 'High level' }) return n;
CREATE (n:Style { name: 'Shape', level: 'High level' }) return n;
CREATE (n:Style { name: 'Elevation', level: 'High level' }) return n;


CREATE (n:Foundations { name: 'Color', level: 'High level', Subclasses: 'Accessibility'}) return n;
CREATE (n:Foundations { name: 'Text', level: 'High level', Subclasses: 'Accessibility, Content'}) return n;
CREATE (n:Foundations { name: 'Label', level: 'High level', Subclasses: 'Accessibility, Content'}) return n;
CREATE (n:Foundations { name: 'Structure', level: 'High level', Subclasses: 'Accessibility'}) return n;
CREATE (n:Foundations { name: 'Flow', level: 'High level', Subclasses: 'Accessibility'}) return n;
CREATE (n:Foundations { name: 'Layout', level: 'High level', Subclasses: 'Accessibility, Layout'}) return n;
CREATE (n:Foundations { name: 'Implement', level: 'High level', Subclasses: 'Accessibility'}) return n;



CREATE (n:Property_Group { name: 'Color', level: 'Middle level' }) return n;
match(a:Foundations {name:'Color'}),(b:Property_Group {name:'Color'}) create (b)<-[r:Accessibility_contrast]-(a) return r;
match(a:Style {name:'Color'}),(b:Property_Group {name:'Color'}) create (b)<-[r:role_utilities]-(a) return r;

CREATE (n:Property_Group { name: 'Text', level: 'Middle level' }) return n;
match(a:Style {name:'Typography'}),(b:Property_Group {name:'Text'}) create (b)<-[r:font]-(a) return r;
match(a:Foundations {name:'Text'}),(b:Property_Group {name:'Text'}) create (b)<-[r:Content_Accessibility_size]-(a) return r;
match(a:Foundations {name:'Structure'}),(b:Property_Group {name:'Text'}) create (b)<-[r:Accessibility_heading]-(a) return r;

CREATE (n:Property_Group { name: 'Label', level: 'Middle level' }) return n;
match(a:Foundations {name:'Label'}),(b:Property_Group {name:'Label'}) create (b)<-[r:Content_Accessibility]-(a) return r;
match(a:Foundations {name:'Structure'}),(b:Property_Group {name:'Label'}) create (b)<-[r:Accessibility_label]-(a) return r;

CREATE (n:Property_Group { name: 'Group', level: 'Middle level' }) return n;
match(a:Foundations {name:'Structure'}),(b:Property_Group {name:'Group'}) create (b)<-[r:Accessibility_landmark]-(a) return r;
match(a:Foundations {name:'Flow'}),(b:Property_Group {name:'Group'}) create (b)<-[r:Accessibility_priority]-(a) return r;
match(a:Foundations {name:'Layout'}),(b:Property_Group {name:'Group'}) create (b)<-[r:Layout]-(a) return r;

CREATE (n:Property_Group { name: 'Clickable', level: 'Middle level' }) return n;
match(a:Foundations {name:'Flow'}),(b:Property_Group {name:'Clickable'}) create (b)<-[r:Accessibility_focus_order]-(a) return r;
match(a:Foundations {name:'Layout'}),(b:Property_Group {name:'Clickable'}) create (b)<-[r:Accessibility_touch_target_size]-(a) return r;
match(a:Style {name:'Elevation'}),(b:Property_Group {name:'Clickable'}) create (b)<-[r:floating_element]-(a) return r;

CREATE (n:Property_Group { name: 'Spacing', level: 'Middle level' }) return n;
match(a:Foundations {name:'Layout'}),(b:Property_Group {name:'Spacing'}) create (b)<-[r:Layout]-(a) return r;

CREATE (n:Property_Group { name: 'Platform', level: 'Middle level' }) return n;
match(a:Foundations {name:'Implement'}),(b:Property_Group {name:'Platform'}) create (b)<-[r:Accessibility]-(a) return r;
match(a:Foundations {name:'Layout'}),(b:Property_Group {name:'Platform'}) create (b)<-[r:Layout]-(a) return r;



# Elements
<!-- Elevation-all elements
Shape-all elements
Icon-icon button -->

CREATE (n:Component { name: 'badges', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'bottom app bar', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'bottom sheets', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'common buttons', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'cards', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'carousel', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'checkbox', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'chips', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'date pickers', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'dialogs', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'divider', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'extended fab', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'floating action button', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'icon buttons', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'lists', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'menus', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'navigation bar', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'navigation drawer', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'navigation rail', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'progress indicators', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'radio button', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'search', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'segmented buttons', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'side sheets', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'sliders', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'snackbar', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'switch', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'tabs', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'text fields', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'time pickers', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'tooltips', level: 'Low level' }) RETURN n;
CREATE (n:Component { name: 'top app bar', level: 'Low level' }) RETURN n;



