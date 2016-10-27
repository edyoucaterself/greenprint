//Function to load form on modal with info from table row

function loadModalForm(modalform, row) { 
    //Get itemnote and id from for 
    var note = row.attr("title");
    var itemid = row.attr("name");

    //Set form path with itemid
    var formpath = "/config/" + itemid + "/";
    $(modalform).attr("action", formpath);
    $("#modalform input[id=id_itemNote]").val(note);

    //Get parentItem and pass
    //find each td element and populate form 
    row.find("td").each(function(){ 
        var data=$(this).text(); 
        var line_id=$(this).attr("name"); 
        console.log(data,line_id); 
        //put value into form 
        var form_input=modalform + " input[id=" + line_id + "]"; 
        $(form_input).val(data); 
    }); 
    
}
