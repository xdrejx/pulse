#version 330 core

out vec4 FragColor;

uniform float barHeights[5]; // Array of heights for the bars
uniform float time; // You might want to use time or some other uniform variable to animate the bars

void main()
{
    // Normalized coordinates of the fragment (from 0 to 1)
    vec2 pos = gl_FragCoord.xy / vec2(1024.0, 768.0);
    
    // Width of each bar and space between them
    float barWidth = 0.1; // 10% of the width of the viewport
    float spacing = 0.05; // 5% of the width of the viewport

    // Calculate positions for bars
    float barPos = 0.1;

    // Determine if we are within the width of each bar and its height
    bool inBar = false;

    for (int i = 0; i < 5; ++i) {
        bool inThisBar = pos.x > barPos && pos.x < barPos + barWidth;
        bool inThisBarHeight = pos.y < barHeights[i];

        if (inThisBar && inThisBarHeight) {
            inBar = true;
            break;
        }

        barPos += barWidth + spacing;
    }

    // Color the fragment black if it's within the height of a bar, otherwise white
    if (inBar) {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0); // Black color for bars
    } else {
        FragColor = vec4(1.0, 1.0, 1.0, 1.0); // White color for background
    }
}
