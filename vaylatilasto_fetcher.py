# Lisää tähän loopiin joka käy tulokset läpi:
for score in scores: # score = heitto per väylä
    if score == 1:
        hole_data["hio"] = hole_data.get("hio", 0) + 1
