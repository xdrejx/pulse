#version 330 core

out vec4 FragColor;

uniform float bar1, bar2, bar3, bar4, bar5; // Heights of the bars controlled by these variables
uniform float time; // You might want to use time or some other uniform variable to animate the bars

void main()
{
    // Normalized coordinates of the fragment (from 0 to 1)
    vec2 pos = gl_FragCoord.xy / vec2(1024.0, 768.0);
    
    // Width of each bar and space between them
    float barWidth = 0.1; // 10% of the width of the viewport
    float spacing = 0.05; // 5% of the width of the viewport

    // Calculate positions for bars
    float bar1Pos = 0.1;
    float bar2Pos = bar1Pos + barWidth + spacing;
    float bar3Pos = bar2Pos + barWidth + spacing;
    float bar4Pos = bar3Pos + barWidth + spacing;
    float bar5Pos = bar4Pos + barWidth + spacing;

    // Determine if we are within the width of each bar
    bool inBar1 = pos.x > bar1Pos && pos.x < bar1Pos + barWidth;
    bool inBar2 = pos.x > bar2Pos && pos.x < bar2Pos + barWidth;
    bool inBar3 = pos.x > bar3Pos && pos.x < bar3Pos + barWidth;
    bool inBar4 = pos.x > bar4Pos && pos.x < bar4Pos + barWidth;
    bool inBar5 = pos.x > bar5Pos && pos.x < bar5Pos + barWidth;

    // Determine the height of each bar
    bool inBar1Height = pos.y < bar1;
    bool inBar2Height = pos.y < bar2;
    bool inBar3Height = pos.y < bar3;
    bool inBar4Height = pos.y < bar4;
    bool inBar5Height = pos.y < bar5;

    // Color the fragment black if it's within the height of a bar, otherwise white
    if ((inBar1 && inBar1Height) || 
        (inBar2 && inBar2Height) ||
        (inBar3 && inBar3Height) ||
        (inBar4 && inBar4Height) ||
        (inBar5 && inBar5Height))
    {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0); // Black color for bars
    }
    else
    {
        FragColor = vec4(1.0, 1.0, 1.0, 1.0); // White color for background
    }
}
