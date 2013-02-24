mybuys.setClient("OREILLY");
mybuys.enableZones();

mybuys.setStyle('.mbpricerowleft','float','');
mybuys.setStyle('.mbpricerowright','float','');
mybuys.setStyle('.mbzone','width','100%', 'padding','0 10px');
mybuys.setStyle('.mbitem','width','100%','padding-right','0px','padding-left','0px','padding-top','5px');
mybuys.setStyle('.mbnamelink:link','color','#0000ff','font-size','11px','font-weight','bold','text-decoration','none','font-family', 'verdana, arial, helvetica');
mybuys.setStyle('.mbnamelink:visited','font-family', 'verdana, arial, helvetica','color','#551A8B','font-size','11px','font-weight','bold','text-decoration','none');
mybuys.setStyle('.mbnamelink:hover','font-family', 'verdana, arial, helvetica','color','#0000ff','font-size','11px','font-weight','bold','text-decoration','none');
mybuys.setStyle('.mbnamerowspan','margin-top','5px');
mybuys.setStyle('.mbpricelink:link','font-family', 'verdana, arial, helvetica','color','#222222','font-size','11px','font-weight','normal','text-decoration','none');
mybuys.setStyle('.mbpricelink:visited','font-family', 'verdana, arial, helvetica','color','#222222','font-size','11px','font-weight','normal','text-decoration','none');
mybuys.setStyle('.mbpricelink:hover','font-family', 'verdana, arial, helvetica','color','#222222','font-size','11px','font-weight','normal','text-decoration','none');
mybuys.setStyle('.mbpricerowspan','text-align','center');
mybuys.setStyle('.mbpricelinklabel:link','font-family', 'verdana, arial, helvetica','color','#222222','font-size','11px','font-weight','normal','text-decoration','none');
mybuys.setStyle('.mbpricelinklabel:visited','font-family', 'verdana, arial, helvetica','color','#222222','font-size','11px','font-weight','normal','text-decoration','none');
mybuys.setStyle('.mbpricelinklabel:hover','font-family', 'verdana, arial, helvetica','color','#222222','font-size','11px','font-weight','normal','text-decoration','none');

/* Content1 specifics */
mybuys.setStyle('.mbzone_content1');
mybuys.setStyle('.mbpricerowleft_content1','float','none','text-align','right','height','12px');
mybuys.setStyle('.mbpricerowright_content1','float','none','text-align','center','height','12px');
mybuys.setStyle('.mbitem_content1','font-size','11px','width','100%','padding-bottom','26px','text-align','left');
mybuys.setStyle('.mbnamerowspan_content1','text-align','left','float','left','width','100%','display','block','margin-top','5px');
mybuys.setStyle('.mbpricerowspan_content1','text-align','left','float','left','width','100%','display','block','height','16px');
mybuys.setStyle('.mbpricelink_content1:link','font-family', 'verdana, arial, helvetica, sans-serif','color','#000000','font-size','11px','font-weight','normal','text-decoration','none');
mybuys.setStyle('.mbpricelink_content1:visited','font-family', 'verdana, arial, helvetica, sans-serif','color','#000000','font-size','11px','font-weight','normal','text-decoration','none');
mybuys.setStyle('.mbpricelink_content1:hover','font-family', 'verdana, arial, helvetica, sans-serif','color','#000000','font-size','11px','font-weight','normal','text-decoration','none');

// new zones 
mybuys.setStyle('.mbzone2 .mbzonetitle', 'color','#333333','font-size','13px','font-weight','bold','font-family', 'arial, helvetica, verdana');
mybuys.setStyle('.mbzone2 .mblegend', 'border-bottom','1px solid #D9D9D9', 'background-color', '#d7d7d7')
mybuys.setStyle('.mbzone2 .mbitem','margin', '5px 0px 10px 0px');
mybuys.setStyle('.mbzone2 .mbnamelink:link','color','#207CC1','font-size','14px','font-weight','bold','text-decoration','none','font-family', 'arial, helvetica, verdana');
mybuys.setStyle('.mbzone2 .mbnamelink:visited','color','#207CC1','font-size','14px','font-weight','bold','text-decoration','none','font-family', 'arial, helvetica, verdana');
mybuys.setStyle('.mbzone2 .mbnamelink:hover','color','#207CC1','font-size','14px','font-weight','bold','text-decoration','underline','font-family', 'arial, helvetica, verdana');
mybuys.setStyle('.mbzone2 .mbpricerowspan', 'color','#333333','font-size','12px','font-weight','bold')
mybuys.setStyle('.mbzone2 .mbpricelink:link','font-family', 'arial, helvetica, verdana','color','#333333','font-size','12px','font-weight','bold','text-decoration','none');
mybuys.setStyle('.mbzone2 .mbpricelink:visited','font-family', 'arial, helvetica, verdana','color','#333333','font-size','12px','font-weight','bold','text-decoration','none');
mybuys.setStyle('.mbzone2 .mbpricelink:hover','font-family', 'arial, helvetica, verdana','color','#333333','font-size','12px','font-weight','bold','text-decoration','none');
mybuys.setStyle('.mbzone2 .mbpricelinklabel:link','font-family', 'arial, helvetica, verdana','color','#333333','font-size','12px','font-weight','normal','text-decoration','none');
mybuys.setStyle('.mbzone2 .mbpricelinklabel:visited','font-family', 'arial, helvetica, verdana','color','#333333','font-size','12px','font-weight','normal','text-decoration','none');
mybuys.setStyle('.mbzone2 .mbpricelinklabel:hover','font-family', 'arial, helvetica, verdana','color','#333333','font-size','12px','font-weight','normal','text-decoration','none');

mybuys.setStyleByPageType('HOME', '.mbzone2','width','240px','border','1px solid #D9D9D9', 'padding', '0');
mybuys.setStyleByPageType('HOME', '.mbzone2 .mbitem','width','200px', 'padding', '0 19px');

mybuys.setStyleByPageType('NEW', '.mbzone2','width','230px', 'border','1px solid #D9D9D9', 'padding', '0');
mybuys.setStyleByPageType('NEW', '.mbzone2 .mbitem','width','200px', 'padding', '0 14px');
mybuys.setStyleByPageType('LANDING', '.mbzone2','width','230px', 'border','1px solid #D9D9D9', 'padding', '0');
mybuys.setStyleByPageType('LANDING', '.mbzone2 .mbitem','width','200px', 'padding', '0 14px');
mybuys.setStyleByPageType('HIGH_LEVEL_CATEGORY', '.mbzone2','width','230px', 'border','1px solid #D9D9D9', 'padding', '0');
mybuys.setStyleByPageType('HIGH_LEVEL_CATEGORY', '.mbzone2 .mbitem','width','200px', 'padding', '0 14px');
mybuys.setStyleByPageType('SHOPPING_CART', '.mbzone2','width','230px', 'border','1px solid #D9D9D9', 'padding', '0');
mybuys.setStyleByPageType('SHOPPING_CART', '.mbzone2 .mbitem','width','200px', 'padding', '0 14px');

mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2','width','596px', 'border','1px solid #D9D9D9');
mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2 .mblegend', 'text-align','left')
mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2 .mbitem','width','150px', 'padding-left', '12px', 'padding-right', '32px');
mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2 .mbnamerowspan','text-align','left');
mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2 .mbnamelink:link','font-weight','bold');
mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2 .mbnamelink:visited','font-weight','bold');
mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2 .mbnamelink:hover','font-weight','bold');
mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2 .mbimgspan','text-align','left');
mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2 .mbpricerowspan','text-align','left');
mybuys.setStyleByPageType('ADD_TO_CART', '.mbzone2 .mbrating', 'text-align', 'left');

mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2','width','670px', 'padding-left', '12px');
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mblegend', 'border-bottom','0px solid #D9D9D9', 'padding', '0')
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mbzonetitle', 'font-size', '0px');
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mbitem','width','150px', 'padding-right', '76px');
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mbnamerowspan','text-align','left');
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mbnamelink:link','font-weight','bold');
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mbnamelink:visited','font-weight','bold');
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mbnamelink:hover','font-weight','bold');
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mbimgspan','text-align','left');
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mbpricerowspan','text-align','left');
mybuys.setStyleByPageType('PRODUCT_DETAILS', '.mbzone2 .mbrating', 'text-align', 'left');

mybuys.useOneclkForExistingSignup(false);
mybuys.applyStyles();
mybuys.setFailOverMsecs(8000);

