//Function to load form on modal with info from table row

function loadModalForm(modalform, row) { 
    //Get itemnote and id from for 
    var itemid = row.attr("name");

    //Set form path with itemid
    var formpath = "/config/" + itemid + "/";
    $(modalform).attr("action", formpath);

    //Get cycle, if single set #radios attr style to "display:none;"
    var cycle = $('[name="' + itemid +'_cycle"]').text();
    if (cycle == "Single"){
        $('#radios').attr("style","display:none");
        console.log("Single Item");
    } else {
        $('#radios').attr("style","");
    }
    //console.log('test' + cycle);

    //Get parentItem and pass
    //find each td element and populate form 
    row.find("td").each(function(){ 
        var data=$(this).text(); 
        var line_id=$(this).attr("name"); 
        //console.log(line_id, data); 
        //put value into form 
        var form_input=modalform + " input[id=" + line_id + "]"; 
        $(form_input).val(data); 
    }); 
    
}
