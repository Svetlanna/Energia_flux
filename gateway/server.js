const express = require("express");

const app = express();
app.use(express.json());

const PORT = 3000;
const URL_SERVICE_PREDICTION = "http://127.0.0.1:8000/predict";

app.post("/api/prediction", async (req, res) => {
const { heure, jour_semaine, mois, weekend, temperature, humidite } = req.body;

  try {
    const reponse = await fetch(URL_SERVICE_PREDICTION, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
  heure, jour_semaine, mois, weekend, temperature, humidite,
}),
    });

    if (!reponse.ok) {
      const erreur = await reponse.json();
      return res.status(reponse.status).json({
        erreur: "Le service de prediction a renvoye une erreur",
        details: erreur,
      });
    }

    const prediction = await reponse.json();
    res.json(prediction);
  } catch (erreur) {
    res.status(502).json({
      erreur: "Impossible de contacter le service de prediction",
      details: erreur.message,
    });
  }
});

app.listen(PORT, () => {
  console.log(`Gateway demarre sur http://127.0.0.1:${PORT}`);
});