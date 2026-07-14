
var  courses = [
        {
            "title": "graph",
            "description": "graph algorithms",
            "time": "12 days",
            "level": "beginner",
            "url" : "'https://www.google.com'"
        },
        {
            "title": "graph colouring",
            "description": "graph colouring algorithms",
            "time": "5 days",
            "level": "advanced",
            "url" : "'https://www.google.com'"
        }
    ];


var title;
var description;
var time;
var level;
var url;
var course_container=document.getElementById('course_cntainer');

for(i=0 ;i<courses.length;i++){
  //store data into variables
    title=courses[i].title;
    description=courses[i].description;
    time=courses[i].time;
    level=courses[i].level;
    url=courses[i].url;
//add the new element as a child of the courses container

    var course_item='<div onclick="location.href='+url+';" class="course_item"> <p class="course_duration">'+time+'</p><h3 class="course_title">'+title+'</h3><p class="course_description">'+description+'</p><p class="course_level">'+level+'</p></div>';
    course_container.innerHTML+=course_item;
}

// search bar code
const searchBar = document.forms['search-courses'].querySelector('input');
searchBar.addEventListener('keyup',function(e){
  const term = e.target.value.toLowerCase();
  const courses=document.getElementsByClassName('course_title');
  Array.from(courses).forEach(function(course){
    const title = course.textContent;
    if(title.toLowerCase().indexOf(term)!=-1){
      course.parentElement.style.display='block';
    }else {
      course.parentElement.style.display='none';
    }
  })
})
