$('document').ready(function () {
    fetchAccessToken(initializeSyncClient)
});

function fetchAccessToken(handler) {
    $.getJSON('/token?username=dotun', function (data) {
        handler(data);
    });
}

function initializeSyncClient(tokenResponse) {
    var syncClient = new Twilio.Sync.Client(tokenResponse.token)  

    syncClient.list('twilio_incoming_sms').then(function(list) {
        list.getItems().then(function(pages) {
            for(const page of pages.items) {
                const data = page.value;
                addRowToTable(data);
            }
        });

        list.on('itemAdded', function(pages) {
            const data = pages.item.data.value;
            addRowToTable(data);
          });
      });
}

function addRowToTable(data) {
  const markup = `<tr><td>${data.MessageSid}</td><td>${data.From}</td><td>${data.To}</td><td>${data.Message}</td></tr>`
  $("table tbody").append(markup)
  return;
}