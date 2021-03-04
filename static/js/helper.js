// {% for question in latest_question_list %}
//     <form>
//         <div class="row">
//             <div class="col-topic">
//                 <label>{{ question.question_text }}</label>
//             </div>
//             {% for choice in question.choices.all %}
//                 <div class="col-select">
//                     <input type="radio" name="choice" value="{{ choice.id }}" />
//                     <label for="choice{{ forloop.counter }}">{{ choice.choice_text }}</label><br />
//                 </div>
//             {% endfor %}
//         </div>
//     </form>
// {% endfor %}
// <input id="submit-btn" type="submit" value="Vote" />

// <script>
    $(document).on('click', '#submit-btn', function(event){
        var response_data = []
        var question_objs = $('.col-topic');
        var choice_objs = $('.col-select');

        for(i=0;i<question_objs.length;i++){
            var question_text = $(question_objs[i]).find('label').text();
            var choice_id = $(choice_objs[i]).find('input').val();
            var choice_text = $(choice_objs[i]).find('label').text();
            var question_choice = {
                "question_text": question_text,
                "choice_id": choice_id,
                "choice_text": choice_text
            }
            response_data.push(question_choice);
        }
        $.ajax({
            type: "POST",
            url: "url_to_your_view",
            data: response_data,
            success: function(response){
                alert("Success");
            }
        });
    });
// </script>

// def question_choice_view(request):
//     if request.method == "POST":
//         question_choice_data = request.POST['data']
//         # further logic