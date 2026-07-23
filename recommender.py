import pandas as pd


class TrekRecommender:

    def __init__(self, csv_file="clean_treks.csv"):
        self.df = pd.read_csv(csv_file)

    # ---------------------------------------
    # AI Explanation
    # ---------------------------------------
    def generate_explanation(
        self,
        trek,
        budget,
        days,
        month,
        experience,
        reasons
    ):

        overview = str(trek.get("Overview", "")).lower()

        keyword_map = {
            "snow": "snow-covered trails",
            "glacier": "spectacular glaciers",
            "lake": "beautiful alpine lakes",
            "forest": "dense Himalayan forests",
            "meadow": "lush alpine meadows",
            "flower": "vibrant flower valleys",
            "summit": "a rewarding summit climb",
            "peak": "stunning Himalayan peaks",
            "river": "beautiful mountain rivers",
            "camp": "memorable campsites",
            "ridge": "panoramic ridge walks",
            "waterfall": "beautiful waterfalls"
        }

        highlights = []

        for key, value in keyword_map.items():
            if key in overview:
                highlights.append(value)

        highlights = list(dict.fromkeys(highlights))

        explanation = (
            f"After comparing your preferences with every available trek, "
            f"**{trek['Trek']}** emerged as one of your strongest matches.\n\n"
        )

        explanation += (
            "It was recommended because:\n"
        )

        for reason in reasons:
            explanation += f"- {reason}\n"

        if highlights:

            explanation += "\n### 🌟 What you'll experience\n"

            for item in highlights[:4]:
                explanation += f"- {item}\n"

        explanation += (
            "\nThis recommendation balances your budget, available days, "
            "preferred season and trekking experience to maximize your overall experience."
        )

        return explanation

    # ---------------------------------------
    # Main Recommendation Function
    # ---------------------------------------
    def recommend(self, budget, days, month, experience):

        results = []

        for _, trek in self.df.iterrows():

            score = 0
            reasons = []

            # -------------------------
            # Budget (20)
            # -------------------------

            if pd.notna(trek["Price"]):

             diff = abs(budget - trek["Price"])

             budget_score = min(20, max(0, 20 - (diff / budget) * 20))

             score += budget_score

             if trek["Price"] <= budget:
              reasons.append("Fits within your budget.")
             elif diff <= 2000:
               reasons.append("Slightly above budget.")
                    

            # -------------------------
            # Duration (15)
            # -------------------------

            if pd.notna(trek["Duration"]):

             diff = abs(days - trek["Duration"])

             duration_score = max(0, 15 - diff * 3)

             score += duration_score

             if diff == 0:
              reasons.append("Perfect duration match.")
             elif diff <= 2:
               reasons.append("Close to your preferred duration.")

            # -------------------------
            # Best Month (15)
            # -------------------------

            if month.lower() in str(trek["Best Time"]).lower():

                score += 15

                reasons.append(
                    f"{month} is one of the best months for this trek."
                )

           # -------------------------
           # Experience (40)
           # -------------------------

            difficulty = {
                "easy": 1,
                "easy to moderate": 2,
                "moderate": 3,
                "moderate to difficult": 4,
                "difficult": 5
            }

            preferred = {
                "first-trek": 1,
                "beginner": 2,
                "intermediate": 3,
                "experienced": 5
            }

            grade = str(trek["Grade"]).lower()

            trek_level = 3  # Default

            # Find the matching difficulty level
            for key in sorted(difficulty.keys(), key=len, reverse=True):
                if key in grade:
                    trek_level = difficulty[key]
                    break

            user_level = preferred[experience]

            difference = abs(user_level - trek_level)

            experience_score = max(0, 40 - difference * 10)

            score += experience_score

            if difference == 0:
                reasons.append("Excellent match for your experience level.")

            elif difference == 1:
                reasons.append("Very close to your preferred difficulty.")

            elif trek_level > user_level:
                reasons.append("A slightly more challenging trek than your experience level.")

            else:
                reasons.append("An easier trek that still matches your other preferences.")
                    

            # -------------------------
            # Scenic Bonus (10)
            # -------------------------

            overview = str(trek.get("Overview", "")).lower()

            scenic_keywords = [
                "lake",
                "snow",
                "glacier",
                "flower",
                "meadow",
                "forest",
                "summit",
                "ridge"
            ]

            scenic_score = 0

            for word in scenic_keywords:

                if word in overview:
                    scenic_score += 2

            score += min(scenic_score, 10)

            # -------------------------
            # Safe values
            # -------------------------

            altitude = (
                trek["Max Altitude"]
                if pd.notna(trek["Max Altitude"])
                else 0
            )

            distance = (
                trek["Trekking Distance"]
                if pd.notna(trek["Trekking Distance"])
                else "N/A"
            )

            image = trek["Image"] if "Image" in trek else ""

            explanation = self.generate_explanation(
                trek,
                budget,
                days,
                month,
                experience,
                reasons
            )

            results.append({

                "Trek": trek["Trek"],

                "Image": image,

                "Price": trek["Price"],

                "Duration": trek["Duration"],

                "Altitude": altitude,

                "Distance": distance,

                "Grade": trek["Grade"],

                "Best Time": trek["Best Time"],

                "Score": round(score),

                "Reasons": reasons,

                "Explanation": explanation

            })

        recommendations = pd.DataFrame(results)

        recommendations = recommendations.sort_values(
            by="Score",
            ascending=False
        )
        max_score = recommendations["Score"].max()
        min_score = recommendations["Score"].min()

        if max_score != min_score:
          recommendations["Score"] = (
         85 
         + (
            (recommendations["Score"] - min_score)
            / (max_score - min_score)
        ) * 14
        ).round().astype(int)
        else:
          recommendations["Score"] = 95
         
        return recommendations.head(3)