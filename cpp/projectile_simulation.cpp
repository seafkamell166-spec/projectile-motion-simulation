#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>

using namespace std;

const double G = 9.80;              // gravitational acceleration in m/s^2
const double INITIAL_SPEED = 30.0;  // initial speed in m/s
const double PI = 3.14159265358979323846;

struct ProjectileResult {
    double angle;
    double vx0;
    double vy0;
    double flightTime;
    double range;
    double maxHeight;
};

double degreesToRadians(double degrees) {
    return degrees * PI / 180.0;
}

ProjectileResult calculateProjectile(double speed, double angleDegrees) {
    double angleRadians = degreesToRadians(angleDegrees);

    double vx0 = speed * cos(angleRadians);
    double vy0 = speed * sin(angleRadians);

    double flightTime = (2.0 * vy0) / G;
    double horizontalRange = vx0 * flightTime;
    double maxHeight = (vy0 * vy0) / (2.0 * G);

    ProjectileResult result;
    result.angle = angleDegrees;
    result.vx0 = vx0;
    result.vy0 = vy0;
    result.flightTime = flightTime;
    result.range = horizontalRange;
    result.maxHeight = maxHeight;

    return result;
}

int main() {
    vector<double> angles = {20, 30, 45, 60, 70};
    vector<ProjectileResult> results;

    double bestRange = -1.0;
    double bestAngle = 0.0;

    cout << "Projectile Motion Simulation" << endl;
    cout << "--------------------------------" << endl;
    cout << "Initial speed: " << INITIAL_SPEED << " m/s" << endl;
    cout << "Gravity: " << G << " m/s^2" << endl << endl;

    cout << fixed << setprecision(2);
    cout << setw(8) << "Angle" << " | "
         << setw(8) << "Vx0" << " | "
         << setw(8) << "Vy0" << " | "
         << setw(8) << "Time" << " | "
         << setw(8) << "Range" << " | "
         << setw(12) << "Max Height" << endl;

    cout << string(76, '-') << endl;

    for (double angle : angles) {
        ProjectileResult result = calculateProjectile(INITIAL_SPEED, angle);
        results.push_back(result);

        cout << setw(8) << result.angle << " | "
             << setw(8) << result.vx0 << " | "
             << setw(8) << result.vy0 << " | "
             << setw(8) << result.flightTime << " | "
             << setw(8) << result.range << " | "
             << setw(12) << result.maxHeight << endl;

        if (result.range > bestRange) {
            bestRange = result.range;
            bestAngle = result.angle;
        }
    }

    cout << endl;
    cout << "Observations:" << endl;
    cout << "- The 45 degree launch gives the greatest horizontal range." << endl;
    cout << "- Angles 30 and 60 degrees give the same range." << endl;
    cout << "- Angles 20 and 70 degrees give the same range." << endl;
    cout << "- Higher angles produce greater height and longer flight time." << endl;

    cout << endl;
    cout << "Conclusion: The simulation confirms that projectile motion can be "
         << "separated into horizontal constant-velocity motion and vertical "
         << "constant-acceleration motion." << endl;

    cout << endl;
    cout << "Best range in this test: " << bestRange
         << " m at " << bestAngle << " degrees." << endl;

    return 0;
}
