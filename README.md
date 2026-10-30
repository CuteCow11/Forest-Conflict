# 🐯 Chandrapur Wildlife Conflict Dashboard

An AI-powered dashboard for tracking and predicting human-wildlife conflict incidents around the Tadoba-Andhari Tiger Reserve, Chandrapur, Maharashtra.

## Features
- 📍 Interactive incident map with color-coded animal markers
- 🌡️ Heatmap showing conflict density zones
- 📊 Filterable data table (by date, animal, severity)
- 🔮 ML-powered hotspot predictor (Random Forest)
- Real Tadoba core zone + Andhari buffer zone boundaries

## Project Structure
```
wildlife_conflict/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Dependencies
├── README.md
├── data/
│   ├── generate_data.py    # Dataset generation
│   └── conflict_data.csv   # Generated dataset (auto-created)
├── model/
│   └── train.py            # Random Forest model
└── utils/
    ├── map_utils.py        # Folium map builders
    └── filters.py          # Sidebar filters + stats
```

## Setup

1. Clone the repo and navigate to the folder:
```bash
cd wildlife_conflict
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

The dataset is auto-generated on first run. No manual data setup needed.

## ML Model
- **Algorithm**: Random Forest Classifier
- **Features**: Location (lat/lon), Month, Season, Village, Severity
- **Target**: Animal type (Tiger / Leopard / Elephant / Wild Boar / Sloth Bear)
- **Training**: 80/20 train-test split + 5-fold cross validation
- **Overfitting prevention**: max_depth=8, min_samples_leaf=5

## Built with
- Streamlit — dashboard UI
- Folium — interactive maps
- scikit-learn — ML model
- Pandas / NumPy — data processing