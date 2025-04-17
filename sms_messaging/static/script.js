const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID"
  };
  
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();
  
async function fetchAndVisualize() {
    const requestCounts = {};
  
    const snapshot = await db.collection("service requests").get();
    snapshot.forEach(doc => {
      const data = doc.data();
      const type = data["Request Type"] || "Unknown";
      requestCounts[type] = (requestCounts[type] || 0) + 1;
    });
  
    const labels = Object.keys(requestCounts);
    const values = Object.values(requestCounts);
  
    const ctx = document.getElementById("categoryChart").getContext("2d");
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Number of Requests by Type',
          data: values
        }]
      }
    });
}
  
fetchAndVisualize();

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