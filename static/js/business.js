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
    const hoursList = data.hours[0].open
    const resultList = [];
    const string = ""
    for(const day of hoursList){
        const sched =`<div>Day: ${day.day} - Start: ${day.start}, End: ${day.end}
        </div>`;
        resultList.push(
           sched 
        );
    }
    return resultList.join("");
  }

function printHello(){
    return "hello";
}
// function to store data from API call then format into template literal
function construct(data){
    const hoursList = data.hours[0].open
    // console.log(hoursList)
    for(const day of hoursList){
        // console.log(day.start)
    }
    
    const name = data.name
    const phone = data.display_phone
    const location = data.location.display_address
    const firstImageURL = data.photos[1]
    const secondImageURL = data.photos[2]
    const price = data.price
    const rating = data.rating
    const reviewCount = data.review_count
    const category = data.categories[0].title


    return `<div class="information box"><h4>${name} (${category})</h4><br><h5>Price: ${price}<br>Business Rating: ${rating}<br>Reviews: ${reviewCount}<br>
    <h5>Address: ${location}<br>Phone: ${phone}<br>Hours: ${getHours(data)}
    </h5><br><h5>Photos: </h5><br><img src="${firstImageURL}" width="300" height="300"> <img src="${secondImageURL}" width="300" height="300"></div>`

}