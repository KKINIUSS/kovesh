  	function getResultTest() {
  	console.log(1),
    $.ajax({
        url: '/api/v1/asck/add',
        type: 'POST',
        dataType: 'json',
        contentType: "application/json",
        data :
            JSON.stringify({
                "questionNumber": parseInt(questionNumber),
                "attempts":1,
                "result": question,
                "time": getSec(date1,date2),
                "quiz":{
                    "id" : 1,
                    "date": "12/12/12",
                    "user":{
                        "id": 1,
                        "deleted": false,
                        "name": "name",
                        "age": "userAge",
                        "email": "userEmail",
                        "date": "dateNow()",
                        "gender": "userGender",
                    }
                }
            }),
        success: function(result) {
            data = result.data;
            }
            });
}
