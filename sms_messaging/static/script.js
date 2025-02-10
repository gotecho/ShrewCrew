function filterTable(columnIndex) {
    let input, filter, table, tr, td, i, txtValue;
    
    input = document.getElementsByClassName("filter-input")[columnIndex]; 
    filter = input.value.toLowerCase(); // Convert filter to lowercase for case-insensitive search
    table = document.getElementById("smsTable");
    tr = table.getElementsByTagName("tr");

    for (i = 1; i < tr.length; i++) {  // Start from index 1 to skip header row
        td = tr[i].getElementsByTagName("td")[columnIndex];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toLowerCase().indexOf(filter) > -1) {
                tr[i].style.display = ""; // Show row
            } else {
                tr[i].style.display = "none"; // Hide row
            }
        }
    }
}