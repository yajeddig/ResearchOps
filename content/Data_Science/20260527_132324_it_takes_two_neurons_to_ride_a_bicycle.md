---
title: "It Takes Two Neurons To Ride a Bicycle"
date: 2026-05-27
category: Data_Science
confidence: 0.95
tags: ['control systems', 'neural networks', 'reinforcement learning', 'robotics', 'simulation', 'bicycle dynamics', 'machine learning', 'autonomous systems', 'control theory']
source: "https://fermatslibrary.com/s/it-takes-two-neurons-to-ride-a-bicycle#email-newsletter"
type: Article
source_type: Paper
hash: 132324
---

## 🎯 Relevance
This content is highly useful for understanding the application of simple neural networks and control theory in robotics and automation. It provides valuable insights into the challenges of reinforcement learning (especially value function design) and demonstrates how human-derived heuristics can lead to robust and efficient controllers. This is directly applicable to industrial automation, autonomous systems, and process control where robust and interpretable models are often preferred over complex, black-box solutions. It also highlights a learning opportunity in designing effective control strategies and the trade-offs between different AI/ML approaches.

## 📖 Content
This paper presents a novel approach to controlling a virtual bicycle using a two-neuron network, contrasting it with traditional reinforcement learning (RL) methods and human control. The authors highlight the counter-intuitive nature of bicycle control, even for humans in a simulated environment.

## 1 Introduction
The challenge of riding a bicycle, for humans or computers, lacks clear intuitive advice. The author's personal experience with a virtual bicycle simulator revealed the counter-intuitive nature of steering (e.g., pushing handlebars left to turn right initially).

## 2 Methodology: Overview of the Simulator System
### 2.1 The Physics
A general robot simulator was developed to experiment with different bicycle controllers. It handles rigid body dynamics, calculating moments of inertia, simulating motion under forces, and solving systems of equations for hinge-like connections.

### 2.2 The Bicycle Robot
The virtual bicycle consists of four rigid bodies: two wheels, the frame, and the front fork. These are connected by rotational joints. Wheels are constrained to the ground without sliding. The controller has access to sensory inputs like position, heading, speed, handlebar angle, lean angle ($\gamma$), and their rates of change ($\dot{\theta}$, $\dot{\gamma}$). Actuators allow torque on the back wheel and handlebars. The controller does not know the bicycle's specific proportions or masses.

### 2.3 The Controller
Three main controller styles were explored:

## 3 The Prescient Controller: A Look at Reinforcement Learning
This controller 'cheats' by having access to the simulator to predict outcomes of actions (push left, push right, no push). It's essentially one step of policy iteration in RL. While it could learn to stay upright, it often did so by performing 'stunts' (e.g., spinning handlebars) rather than riding normally. Attempts to formulate sensible value functions (rewarding uprightness, speed, or straight-line travel) proved difficult, often leading to undesirable behaviors (stunts, swooping, or falling). This highlights the challenge of designing effective value functions in RL, a problem also observed in other research [1] where thousands of practice rides were needed for 'drunken' behavior.

## 4 The Human Controller
Humans attempted to control the virtual bicycle using a keyboard. This experience was counter-intuitive, confirming the initial observation. Human controllers subjectively found it important to focus on manipulating the bicycle's lean angle ($\gamma$). Data analysis of human rides yielded little useful correlation. However, human descriptions of their control algorithms, focusing on lean angle, became the basis for the two-neuron controller.

## 5 The Two-Neuron Network
Inspired by human insights, a two-neuron network was implemented, proving surprisingly competent. It is continuous in time and values, interpreting a unit's output as a thresholded weighted sum of inputs.

**Inputs to the network:** Desired heading ($\theta_d$), current heading ($\theta$), current lean angle ($\gamma$), and their derivatives ($\dot{\theta}$, $\dot{\gamma}$).

**Control Strategy:** To control the bicycle's heading ($\theta$), the network aims to control its rate of change ($\dot{\theta}$). Figure 3 shows a strong relationship between $\dot{\theta}$ and $\gamma$. Therefore, the strategy is to control $\dot{\theta}$ indirectly by controlling $\gamma$. The handlebar torque actuator has reasonable control over $\dot{\gamma}$. A higher clockwise torque generally causes the bicycle to lean more to the left.

**Network Structure and Equations:**
*   **First Neuron:** Calculates the desired lean angle ($\gamma_d$) based on the difference between desired and current heading.
    $$\gamma_d = \sigma(c_1 \theta_d - c_1 \theta)$$
    where $\sigma$ is a thresholding function to prevent extreme leaning.

*   **Second Neuron:** Calculates the desired handlebar torque ($\tau_h$) based on the desired lean angle, current lean angle, and its rate of change.
    $$\tau_h = c_2 \gamma_d - c_2 \gamma - c_3 \dot{\gamma}$$
    The constants $c_1, c_2, c_3$ need to be set, but the network is not overly sensitive to their precise values, making it easy to get a working system.

## 6 Results
The two-neuron network controller performs remarkably well, successfully navigating a sequence of waypoints (Figure 5). It works across a range of speeds but does not explicitly damp instabilities at very low speeds or sharp turns (which might require a third neuron).

## 7 Future Directions: More Automated Learning
Future work focuses on automated learning and parameter tuning for the network, ideally allowing it to adapt to different bicycles without human intervention or detailed physical knowledge. The authors suggest exploring causal models and belief propagation networks for automatically designing such networks.

## Acknowledgments
Thanks to Shuki Bruck and Erik Winfree. Supported by the "Alpha Project" funded by a grant from the National Human Genome Research Institute (Grant No. P50 HG02370).


## 💡 Key Insights
- A simple two-neuron network can effectively control a complex, non-holonomic system like a bicycle, outperforming complex reinforcement learning approaches in terms of development effort and initial performance.
- Human intuition, even when counter-intuitive in direct control, can provide crucial insights (e.g., focusing on lean angle) for designing robust control algorithms.
- Reinforcement Learning (RL) can be challenging for control problems due to the difficulty in designing appropriate value functions that lead to desired, non-stunt-like behaviors and the extensive learning time required.
- The proposed two-neuron controller leverages the natural stability characteristics of a bicycle by indirectly controlling heading through lean angle, which is directly influenced by handlebar torque.
- Future work aims at automating the learning and parameter tuning process for such controllers, reducing reliance on human design and system-specific knowledge.

## 📚 References
- Matthew Cook, "It Takes Two Neurons To Ride a Bicycle", Fermat's Library, URL: https://fermatslibrary.com/s/it-takes-two-neurons-to-ride-a-bicycle *(source)*
- Randløv, Jette and Alstrøm, Preben. "Learning to Drive a Bicycle using Reinforcement Learning and Shaping", PROCEEDINGS OF THE FIFTEENTH INTERNATIONAL CONFERENCE ON MACHINE LEARNING, 1998, pp.463–471. *(cited)*
- Getz, Neil H. and Marsden, Jerrold E. "Control for an Autonomous Bicycle", IEEE INTERNATIONAL CONFERENCE ON ROBOTICS AND AUTOMATION, 1995. *(cited)*
- von Wissel, D., Nikoukhah, R., Delebecque, F., and Campbell, S.L. "Descriptor Predictive Control: Tracking Controllers for a Riderless Bicycle", PROC. COMPUTATIONAL ENGINEERING IN SYSTEMS APPLICATIONS, Lille, France, 1996, pp.292–297. *(cited)*
- Chen, Chi-Da, and Tsai, C.C. "Steering Control System Design and Implementation of a Riderless Bicycle", JOURNAL OF TECHNOLOGY, vol.16, no.2, pp.243-251 (July 2001). *(cited)*
- Buss, Samuel R. "Accurate and Efficient Simulation of Rigid Body Rotations", JOURNAL OF COMPUTATIONAL PHYSICS, vol.164, no.2, pp.377–406 (November 2000). *(cited)*

## 🏷️ Classification
The paper focuses on designing and implementing a control system for a virtual bicycle using a simple neural network, comparing it with reinforcement learning, which are core topics within machine learning and modeling in Data Science.
