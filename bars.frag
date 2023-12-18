#version 330 core

uniform float iTime;
uniform vec2 iResolution;
uniform float barHeights[256]; // Maximum array size for the bars
uniform int numBars; // Actual number of bars to render

out vec4 FragColor;

void main() {
    // Normalizing the coordinates
    vec2 uv = gl_FragCoord.xy / iResolution.xy;

    // Calculate the width of each bar
    float barWidth = 1.0 / float(numBars);

    // Determine which bar the current pixel belongs to
    int barIndex = int(uv.x / barWidth);

    // Check if the current bar index is less than the actual number of bars to render
    if (barIndex < numBars) {
        // Check if the y coordinate is less than the height of the bar
        if (uv.y < barHeights[barIndex]) {
            // Set the fragment color
            FragColor = vec4(0.0, 0.5, 1.0, 1.0); // Blue color
        } else {
            // Set the background color
            FragColor = vec4(0.0, 0.0, 0.0, 1.0); // Black color
        }
    } else {
        // Set the background color
        FragColor = vec4(0.0, 0.0, 0.0, 1.0); // Black color
    }
}
