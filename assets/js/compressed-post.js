// ===== Scroll to Top ====
 $(window).scroll(function() {
    if ($(this).scrollTop() >= 50) {        // If page is scrolled more than 50px
        $('#scrollBtn').fadeIn(500);    // Fade in the arrow
    } else {
        $('#scrollBtn').fadeOut(500);   // Else fade out the arrow
    }
});
$('#scrollBtn').click(function() {      // When arrow is clicked
    $('body,html').animate({
        scrollTop : 0                       // Scroll to top of body
    }, 500);
});
  // Vote button
  testid = testid.replace("/", "");
  testid = testid.replace("/", "");
  var testid2 = "#" + testid;
  document.getElementById('votebutton').id = testid;
  // NOTE: Scroll performance is poor in Safari
  // - this appears to be due to the events firing much more slowly in Safari.
  //   Dropping the scroll event and using only a raf loop results in smoother
  //   scrolling but continuous processing even when not scrolling
  $(document).ready(function () {
    // Start fitVids
    var $postContent = $(".post-full-content");
    $postContent.fitVids();
    // End fitVids

    var progressBar = document.querySelector('progress');
    var header = document.querySelector('.floating-header');
    var title = document.querySelector('.post-full-title');

    var lastScrollY = window.scrollY;
    var lastWindowHeight = window.innerHeight;
    var lastDocumentHeight = $(document).height();
    var ticking = false;

    function onScroll() {
      lastScrollY = window.scrollY;
      requestTick();
    }

    function onResize() {
      lastWindowHeight = window.innerHeight;
      lastDocumentHeight = $(document).height();
      requestTick();
    }

    function requestTick() {
      if (!ticking) {
        requestAnimationFrame(update);
      }
      ticking = true;
    }

    function update() {
      var trigger = title.getBoundingClientRect().top + window.scrollY;
      var triggerOffset = title.offsetHeight + 35;
      var progressMax = lastDocumentHeight - lastWindowHeight;

      // show/hide floating header
      if (lastScrollY >= trigger + triggerOffset) {
        header.classList.add('floating-active');
      } else {
        header.classList.remove('floating-active');
      }

      progressBar.setAttribute('max', progressMax);
      progressBar.setAttribute('value', lastScrollY);

      ticking = false;
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onResize, false);

    update();
  });

  // show/hide tags   if they excceed one line-
  //in-page links and table of contents
  $('.in_page_link').click(function () {
    event.preventDefault()

    //scroll to the href of the link
    $('html, body').animate({
      scrollTop: $($(this).attr('href')).offset().top
    }, 500);
    return false;

  });

  $(document).ready(function () {

    var taglist_height = $('#taglist').height();
    var tag_height = $('#tag_element').height();
    var q_message = document.createElement('h6');

    if (taglist_height >= 35) {
      $("#more").show();
    }

    $('#more').click(function () {

      $('#text').removeClass("less");
      $("#less").show();
      $(this).hide();
    });

    $('#less').click(function () {
      $('#text').addClass("less");
      $(this).hide();
      $("#more").show();
    });

    //Add icon and colors to question answers
    //click function will be shown if the question is answered correctly
    $('.correct_option').click(function () {

      var icon_check = '<i class="fa fa-check fadeMe" style="margin:5px;color:#33cc33;"></i>';
      var icon_cross = '<i class="fa fa-times fadeMe" style="margin:5px;"></i>';

      if ($(this).children().length < 1) {
        $(this).siblings().children().remove();
        $(this).siblings().prepend(icon_cross);
        $(this).siblings().css({ "color": "coral", "border-color": "coral" });


        $(this).addClass("correct_answer");
        $(this).prepend(icon_check);
        q_message.innerHTML = ("Well done, you are the best.");
        q_message.classList.add("question_message");
        q_message.style.color = "MediumSeaGreen";
        $(this).parents(':eq(0)').prepend(q_message);

        // Show the answer explanation

        if ($(this).parent().siblings(".Answer_explanation").length >= 1) {
          $(this).parent().siblings(".Answer_explanation").css({ "display": "block" });
        }
      }
      $(this).attr('disabled', 'disabled');
    });

    //click function will   show the message if the question is answered incorrectly

    $('.wrong_option').click(function () {
      var icon = '<i class="fa fa-times fadeMe" style="margin:5px;"></i>';

      if ($(this).children().length < 1) {
        $(this).addClass("wrong_answer");

        $(this).prepend(icon);
        q_message.innerHTML = ("No worries, this answer is wrong, you must try again");
        q_message.classList.add("question_message");
        q_message.style.color = "coral";
        $(this).parents(':eq(0)').prepend(q_message);
      }
    });
  })

  //shuffle question
  function shuffle(arra1) {
    var ctr = arra1.length, temp, index;

    // While there are elements in the array
    while (ctr > 0) {
      // Pick a random index

      index = Math.floor(Math.random() * ctr);
      // Decrease ctr by 1
      ctr--;
      // And swap the last element with it

      temp = arra1[ctr];
      arra1[ctr] = arra1[index];
      arra1[index] = temp;
    }
    return arra1;
  }

  //get the options
  var questions = document.getElementsByClassName("questionlist");

  // shuffle the elements , and remove options if they are more than 4
  for (c = 0; c <= questions.length; c++) {

    if(questions[c] === undefined)
      break;

    var index;
    var ctr2 = questions[c].children.length;
    var index;

    while (ctr2 > 4) {
      index = Math.floor(Math.random() * ctr2);
      if (index != 0) {
        questions[c].children[index].remove();

        ctr2--;
      }
    }
    var myArray = [1, 2, 3, 4];
    shuffle(myArray);
    for (i = 0; i <= 3; i++) {
      questions[c].children[i].style.order = myArray[i];
      questions[c].children[i].style.display = "block";
    }
  }

  // Vote for Top writer 2023 OTAC
  $(document).ready(function(){
  var mainlocalStorage = $( this ).attr(testid);
  if(localStorage.getItem(testid) == 'true') {
    $(testid2).html('<i class="fa fa-heart" aria-hidden="true"></i>');
    $(this).addClass("liked");
  }
  $(testid2).click(function(){
    if($(testid2).hasClass("liked")){
      $(testid2).html('<i class="fa fa-heart-o" aria-hidden="true"></i>');
      $(testid2).removeClass("liked");
      var btnStorage=$(this).attr(testid);
      localStorage.removeItem(testid, 'true');
    }else{
      $(testid2).html('<i class="fa fa-heart" aria-hidden="true"></i>');
      $(testid2).addClass("liked");
      var btnStorage=$(this).attr(testid);s
      localStorage.setItem(testid, 'true');
    }
  });
});