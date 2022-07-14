function Trips(){
    const [trips, setTrips] = React.useState([]);

    React.useEffect(() => {
        fetch('/trip-info')
        .then(response => response.json())
        .then(result => {
            setTrips(result);
        });

    }, []);

    // function to delete a trip from trips list
    function deleteTrip(trip_id){
        // fetch request to delete route
        fetch(`/delete_trip/${trip_id}`)
        .then((response) => response.text())
        .then((result) => {
            // create a new list, filter out the trip with the ID we don't want to add
            const newList = trips.filter((trip) => trip.trip_id !== trip_id)
            setTrips(newList)
        })
    }
    const listOfTrips = [];

    for (const trip of trips){
        listOfTrips.push(<li key={trip.name}>
         
            <div className="trip-container">

            <div className="centered">
            <h3>{trip.name } in {trip.city}</h3>
            <hr></hr>
            <h5>{trip.start_date.slice(0,16)} - {trip.end_date.slice(0,16)}</h5>
            <button className="btn btn-light trip-btn" onClick={() => deleteTrip(trip.trip_id)}>Delete Trip</button>
            </div>
            
            <a href={`/trip/${trip.trip_id}`}><img src={`../static/img/${trip.url}`}></img></a>
            </div>
            <br></br>
  
        </li>)
    };

    if (listOfTrips.length == 0){
        return <ul>No trips planned yet.</ul>
    }

    return <ul>{listOfTrips}</ul>;


}
  
  ReactDOM.render(<Trips />, document.querySelector('#root'));