app.get("/product", function(req, res) {
    let id = req.query.id;
    res.send("You requested: " + id);
});

