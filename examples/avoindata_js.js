/*
This is a short example on using the CKAN API of Avoindata.fi
For the CKAN API in general, see http://docs.ckan.org/en/latest/api/index.html
The older docs http://docs.ckan.org/en/ckan-1.7.1/api.html#tools-for-accessing-the-api
also list some tools and libs for accessing the API.

This example displays output via console.log(). See your browser's developer tools to view it.
*/

// Set constants
var base_url = ''; // ie. 'https://beta.avoindata.fi'
var api_key = ''; // log in and see your profile page for your API key

// These actions run asynchronously
organization_list(base_url);

// If your actions depend on each other, you should use a callback chain (or jQuery queue).
create_and_delete_test_organization(base_url, api_key);

// Helper function to handle XMLHttpRequests.
// base_url: ie. 'https://beta.avoindata.fi'
// api_key: log in and see your profile page for your API key
// action: see http://docs.ckan.org/en/latest/api/index.html for possible actions
// payload: JSON string to send with the request
// callback: your own data handling function with one input parameter
function callAPI(base_url, api_key, action, payload, callback) {
  var xmlhttp = new XMLHttpRequest();
  var url = base_url + '/data/api/3/action/' + action;

  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
      response = JSON.parse(xmlhttp.responseText);
      if (response.success == true) { // CKAN may return a result even if request fails
        callback(response.result);
      }
    }
  }
  xmlhttp.open('POST', url, true);
  xmlhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
  if (api_key) {
    xmlhttp.setRequestHeader('X-CKAN-API-KEY', api_key);
  }
  if (payload) {
    xmlhttp.send(payload);
  }
  else {
    xmlhttp.send();
  }
}

// Example of an action without authorization or payload
// Loops over result set and prints organization names to console.log()
function organization_list(base_url) {
  callAPI(base_url, null, 'organization_list', null, function(data) {
    console.log('*** List all organizations ***');
    for (var i = 0; i < data.length; i++) {
      console.log(data[i]);
    }
  });  
}

// Example of actions with authorization and payload
// Example of callback chaining
// Creates an organization with unique name and deletes it
function create_and_delete_test_organization(base_url, api_key) {
  var organization_name = "z-org-apitest-" + Date.now() // API call fails if name is not unique
  var payload = JSON.stringify({
    'name': organization_name,
    'title': 'Z CKAN API ' + organization_name
  });
  callAPI(base_url, api_key, 'organization_create', payload, function(data) {
    console.log('*** Created test organization ' + organization_name + ' ***');
    var payload = JSON.stringify({
      'id': organization_name
    });
    callAPI(base_url, api_key, 'organization_delete', payload, function(data) {
      console.log('*** Deleted test organization ' + organization_name + ' ***');
    });
  });
}