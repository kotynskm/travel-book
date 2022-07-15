// helper function to format phone number for display marker
function formatPhoneNumber(phoneNumberString) {
  var cleaned = ('' + phoneNumberString).replace(/\D/g, '');
  var match = cleaned.match(/^(1|)?(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    var intlCode = (match[1] ? '+1 ' : '');
    return [intlCode, '(', match[2], ') ', match[3], '-', match[4]].join('');
  }
  return null;
}


function initMap() {
    // location to create initial center
    const sf = { lat: 37.601773, lng: -122.20287 };
    // The map, initially centered at san fran 
    const map = new google.maps.Map(document.getElementById("map"), {
      zoom: 10,
      center: sf,
      mapId: 'f709ca57eea4cb19'
    });
    const infoWindow = new google.maps.InfoWindow({
     
      maxWidth: 200,
    })
    // fetch request to map marker route to create markers for map
    fetch(`/map-coordinates/${window.location.href.split("/")[4]}`)
    .then((response) => response.json())
    .then((markers) => {
      for (const marker of markers){
        const mapMarker = new google.maps.Marker({
          position: {
            lat: marker.lat,
            lng: marker.lng,
          },
          title: `${marker.name}`,
          map: map,
        });
      // create an info window for each map marker
        const markerInfo = `<h5>${marker.name}</h5><h6>Address: ${marker.address}${marker.zipcode}</h6><h6>Phone: ${formatPhoneNumber(marker.phone.slice(2))}</h6>`;
    
        // const infoWindow = new google.maps.InfoWindow({
        //   content: markerInfo,
        //   maxWidth: 200,
        // });
    
        mapMarker.addListener('click', () => {
          infoWindow.close();
          infoWindow.setContent(markerInfo)
          infoWindow.open(map, mapMarker);
        });
      }
    
    // overwrite center to first marker location
    map.setCenter(markers[0])
  });

}


