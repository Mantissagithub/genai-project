import React, { useState } from "react";
import "./App.css";

function App() {
  const [initialPrompt, setInitialPrompt] = useState("");
  const [customizingPrompt, setCustomizingPrompt] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setIsGenerating(true);

    try {
      // backend endpoint  - kb
      const response = await fetch(
        "http://localhost:7860/image-generation-base",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            customizingPrompt,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to generate image");
      }

      const data = await response.json();
      //image insertion plave - kb
      setImageUrl("img.png" || "/api/placeholder/400/320");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setTimeout(() => {
        setIsGenerating(false);
      }, 500);
    }
  };

  return (
    <div className="app-container">
      <div className="content-wrapper">
        <div className="left-section">
          <h1>Image Generator</h1>
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label htmlFor="initialPrompt">Initial Prompt</label>
              <textarea
                id="initialPrompt"
                value={initialPrompt}
                onChange={(e) => setInitialPrompt(e.target.value)}
                placeholder="Enter your initial prompt here..."
                rows={5}
              />
            </div>

            <button
              type="button"
              className={`submit-button ${loading ? "button-loading" : ""}`}
              disabled={loading || !initialPrompt.trim()}
              onClick={async (e) => {
                setLoading(true);
                setError(null);
                setIsGenerating(true);

                try {
                  const response = await fetch(
                    "http://localhost:7860/image-generation-base",
                    {
                      method: "POST",
                      headers: {
                        "Content-Type": "application/json",
                      },
                      body: JSON.stringify({
                        initialPrompt,
                      }),
                    }
                  );

                  if (!response.ok) {
                    throw new Error("Failed to generate image");
                  }

                  const data = await response.json();
                  console.log(data);
                  setImageUrl("update_img.png" || "/api/placeholder/400/320");
                } catch (err) {
                  setError(err.message);
                } finally {
                  setLoading(false);
                  setTimeout(() => {
                    setIsGenerating(false);
                  }, 500);
                }
              }}
            >
              <span className="button-text">
                {loading ? "Generating..." : "Generate Base Image"}
              </span>
              <span className="button-animation"></span>
            </button>

            <div className="input-group">
              <label htmlFor="customizingPrompt">Customizing Prompt</label>
              <textarea
                id="customizingPrompt"
                value={customizingPrompt}
                onChange={(e) => setCustomizingPrompt(e.target.value)}
                placeholder="Enter your customizing prompt here..."
                rows={5}
              />
            </div>
            <button
              type="button"
              className={`submit-button ${loading ? "button-loading" : ""}`}
              disabled={loading || !customizingPrompt.trim()}
              onClick={async (e) => {
                setLoading(true);
                setError(null);
                setIsGenerating(true);

                try {
                  const response = await fetch(
                    "http://localhost:7860/image-generation-update",
                    {
                      method: "POST",
                      headers: {
                        "Content-Type": "application/json",
                      },
                      body: JSON.stringify({
                        customizingPrompt,
                      }),
                    }
                  );

                  if (!response.ok) {
                    throw new Error("Failed to generate image");
                  }

                  const data = await response.json();
                  console.log(data);
                  setImageUrl("update_img.png" || "/api/placeholder/400/320");
                } catch (err) {
                  setError(err.message);
                } finally {
                  setLoading(false);
                  setTimeout(() => {
                    setIsGenerating(false);
                  }, 500);
                }
              }}
            >
              <span className="button-text">
                {loading ? "Customizing..." : "Customize Image"}
              </span>
              <span className="button-animation"></span>
            </button>
          </form>
        </div>

        <div className="right-section">
          <h2>Generated Image</h2>
          <div
            className={`image-container ${isGenerating ? "generating" : ""}`}
          >
            {loading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
                <div className="loading-text">Generating your image...</div>
              </div>
            ) : error ? (
              <div className="error-message">{error}</div>
            ) : imageUrl ? (
              <img
                src="update_img.png"
                alt="Generated content"
                className="generated-image"
              />
            ) : (
              <div className="placeholder-message">
                Your generated image will appear here
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
