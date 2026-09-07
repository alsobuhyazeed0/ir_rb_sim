# ir_rb_sim
Open-source Python simulator for infrared-based range-and-bearing (R&B) sensing in swarm robotics.

## Intro

This project provides an open-source simulator for low-cost infrared (IR) range-and-bearing systems used in swarm robotics based on the following literature

> Çeşme, Ibrahim H., and Levent Bayindir. "Low-Cost High-Performance Infrared-Based
> Range and Bearing System for Swarm Robotics." IEEE Access (2026).

The library models sensor geometry, binary-search-based ranging, and bearing estimation, allowing researchers and students to simulate robot swarms without physical hardware.

The goal is to go beyond the hardware paper and use the simulator to test scenarios the physical hardware can't easily test (e.g. scheduling/collision behavior at swarm scale: 10, 50, 100 robots), and report accuracy vs. scale.

## Status

Early development.
