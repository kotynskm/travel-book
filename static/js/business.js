

// select all buttons and result div where data will be displayed
const buttons = document.querySelectorAll('#business-button');
const result = document.querySelector('.result')


for(const button of buttons){
    button.addEventListener('click', (evt) => {
        evt.preventDefault()
        // get the business ID from button
        const businessID = evt.target.value;
        // send business ID to route using URLSearchParams to create a query string
        const business = new URLSearchParams({ business: businessID }).toString();
        const url = `/show-business-info?${business}`;
        fetch(url)
        .then(res => res.json())
        .then(data => {
            result.innerHTML = construct(data); // call function to create data display
    })

    })
};

// function to retrieve hours
function getHours(data) {
    // get list of hours from data
    const hoursList = data.hours[0].open
    const resultList = [];

    for(const day of hoursList){
        // convert day number to actual weekday
        switch (day.day) {
            case 0:
                dayOfWeek = "Sunday";
                break;
            case 1:
                dayOfWeek = "Monday";
                break;
            case 2:
                dayOfWeek = "Tuesday";
                break;
            case 3:
                dayOfWeek = "Wednesday";
                break;
            case 4:
                dayOfWeek = "Thursday";
                break;
            case 5:
                dayOfWeek = "Friday";
                break;
            case 6:
                dayOfWeek = "Saturday";
        }
        const sched =`<div>${dayOfWeek} - Open: ${day.start} | Close: ${day.end}
        </div>`;
        resultList.push(
           sched 
        );
    }
    return resultList.join("");
  }

// function to store data from API call then format into template literal
function construct(data){

    const name = data.name
    const phone = data.display_phone
    const location = data.location.display_address
    const firstImageURL = data.photos[1]
    const secondImageURL = data.photos[2]
    let price = data.price
    if(price == undefined){
        price = "No price listed."
    }
    const rating = data.rating
    const reviewCount = data.review_count
    const category = data.categories[0].title


    return `<div class="information-box"><h4>${name} (${category})</h4><br><h5>Price: ${price}<br>Business Rating: ${rating}<br><br>
    <h5>Address: ${location}<br>Phone: ${phone}<br><br>Hours: ${getHours(data)}
    </h5><br><h5>Photos: </h5><img src="${firstImageURL}" width="300" height="300"> <img src="${secondImageURL}" width="300" height="300"></div>`

}


