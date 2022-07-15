function initMap() {
    // location to create initial center
    const sf = { lat: 37.601773, lng: -122.20287 };
    // The map, initially centered at san fran 
    const map = new google.maps.Map(document.getElementById("main"), {
      zoom: 3,
      center: sf,
      mapId: 'f709ca57eea4cb19'
    });
    const infoWindow = new google.maps.InfoWindow({
     
      maxWidth: 200,
    })
    // fetch request to map marker route to create markers for map
    fetch('/main-map-coordinates')
    .then((response) => response.json())
    .then((markers) => {
      for (const marker of markers){
        const mapMarker = new google.maps.Marker({
          position: {
            lat: marker.lat,
            lng: marker.lng,
          },
          title: `${marker.trip_name}`,
          map: map,
        });
      // create an info window for each map marker
        const markerInfo = `<h4>${marker.trip_name}</h4><h5>${marker.city_name}</h5`;
    
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



  