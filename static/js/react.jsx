function Trips(){
    const [trips, setTrips] = React.useState([]);

    React.useEffect(() => {
        fetch('/trip-info')
        .then(response => response.json())
        .then(result => {
            setTrips(result);
        });

    }, []);

    
    const listOfTrips = [];

    for (const trip of trips){
        listOfTrips.push(<li key={trip.name}>
            <h3>{trip.name } in {trip.city}</h3>
            <h5>{trip.start_date.slice(0,16)} - {trip.end_date.slice(0,16)}</h5>
            <div className='hover'>
            <a href={`/trip/${trip.trip_id}`}><img src={`../static/img/${trip.url}`}></img></a>
            </div>
        </li>)
    };

    if (listOfTrips.length == 0){
        return <ul>No trips planned yet.</ul>
    }

    return <ul>{listOfTrips}</ul>;


}
  
  ReactDOM.render(<Trips />, document.querySelector('#root'));