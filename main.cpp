#include <SFML/Graphics.hpp>
#include <vector>
#include <cmath>
#include <queue>


const int BLOCK_SIZE = 50;
const float DISTANCE_RATIO_CONST = 1;
const int MIN_RENDER_DISTANCE = 5;
const int DISPLAY_WIDTH = 1280;
const int DISPLAY_HEIGHT = 720;

struct EdgeTexture {
	int width;
	int height;
	void* texture_pointer;
	bool has_alpha_channel;
};

struct Edge {
	// point - (x, y) coordinates of the edge
	double* point1;
	double* point2;
	EdgeTexture* texture;
	Edge(double* point1, double* point2, EdgeTexture* texture) : point1(point1), point2(point2), texture(texture) {}
};

struct Object {
	int edges_number;
	Edge* edges;
	int scale;
	Object(int edges_number, Edge* edges, int scale) : edges_number(edges_number), edges(edges), scale(scale) {}
};

struct Intersection {
	double distance;
	Edge* obj;
	int column;
	int* scale;
	Intersection(double distance, Edge* obj, int column, int* scale) : distance(distance), obj(obj), column(column), scale(scale) {}
	Intersection() : distance(0.0), obj(nullptr), column(0) {}
};

double distance(double* point1, double* point2) {
	return std::sqrt(std::pow(point1[0] - point2[0], 2) + std::pow(point1[1] - point2[1], 2));
}


std::vector<Intersection> cast_ray(double ray_ang, double* pos, int objects_number, Object* objects) {

	std::vector<Intersection> intersections; // Store intersections with edges
	for (int obj = 0; obj < objects_number; ++obj) {
		for (int edge = 0; edge < objects[obj].edges_number; ++edge) {
			auto& e = objects[obj].edges[edge];

			double points_y_diff = e.point1[1] - e.point2[1];
			double points_x_diff = e.point1[0] - e.point2[0];
			double view_sin = std::sin(ray_ang);
			double view_cos = std::cos(ray_ang);


			double intersection_point[2];

			if (points_x_diff == 0) {
				if (view_cos == 0) {
					continue; // Both are vertical, no intersection
				}
				else {
					double k = view_sin / view_cos;
					double b = pos[1] - k * pos[0];
					double x = e.point1[0];
					double y = k * x + b;
					intersection_point[0] = x;
					intersection_point[1] = y;
				}
			}
			else {
				if (view_cos == 0) {
					double k = points_y_diff / points_x_diff;
					double b = e.point1[1] - k * e.point1[0];
					double x = pos[0];
					double y = k * x + b;
					intersection_point[0] = x;
					intersection_point[1] = y;

				}
				else {
					double k1 = points_y_diff / points_x_diff;
					double k2 = view_sin / view_cos;
					if (k1 == k2) {
						continue; // Parallel lines, no intersection
					}
					else {
						double b1 = e.point1[1] - k1 * e.point1[0];
						double b2 = pos[1] - k2 * pos[0];
						double x = (b2 - b1) / (k1 - k2);
						double y = k1 * x + b1;
						intersection_point[0] = x;
						intersection_point[1] = y;

					}
				}
			}

			double max_x = std::max(e.point1[0], e.point2[0]);
			double min_x = std::min(e.point1[0], e.point2[0]);

			double max_y = std::max(e.point1[1], e.point2[1]);
			double min_y = std::min(e.point1[1], e.point2[1]);

			double dot_product = (intersection_point[0] - pos[0]) * view_cos + (intersection_point[1] - pos[1]) * view_sin;

			if (intersection_point[0] >= min_x && intersection_point[0] <= max_x &&
				intersection_point[1] >= min_y && intersection_point[1] <= max_y) {
				if (dot_product > 0) {
					double dist = distance(pos, intersection_point);
					if (dist > MIN_RENDER_DISTANCE) {
						double units_per_pixel = distance(e.point1, e.point2) / e.texture->width;
						int column = distance(e.point1, intersection_point) / units_per_pixel;
						column = std::min(column, e.texture->width - 1);
						intersections.push_back(Intersection(dist, &e, column, &objects[obj].scale));
					}
				}
			}
		}
	}

	auto cmp = [](const Intersection& a, const Intersection& b) {
		return a.distance > b.distance;
		};
	std::priority_queue<Intersection, std::vector<Intersection>, decltype(cmp)> pq(cmp, intersections);
	std::vector<Intersection> valid_inters; // Store intersections with edges
	for (; !pq.empty(); pq.pop()) {
		valid_inters.push_back(pq.top());
		if (!pq.top().obj->texture->has_alpha_channel) {
			break;
		}
	}
	return valid_inters;
}


extern "C" {
	__declspec(dllexport) void __cdecl update_image(std::uint8_t* output_pixels, double look_ang, double fov, int rays_number, int screen_width, int screen_height, double* pos, int objects_number, Object* objects) {
		sf::Color background_color(255, 120, 120);
		sf::RenderTexture screen(sf::Vector2u(screen_width, screen_height));
		screen.clear(background_color);

		double ang_between_rays = fov / rays_number;
		double ang = look_ang + fov / 2;
		double scale_ratio_x = static_cast<double>(screen_width) / rays_number;
		double curr_start_x = 0;
		for (int i = 0; i < rays_number; ++i) {
			auto intersections = cast_ray(ang, pos, objects_number, objects);
			ang -= ang_between_rays;

			if (intersections.empty()) {
				curr_start_x += scale_ratio_x;
				continue; // No intersection found
			}
			else {
				for (int j = intersections.size() - 1; j >= 0; --j) {

					auto texture_ptr = static_cast<sf::Image*>(intersections[j].obj->texture->texture_pointer);
					int& width = intersections[j].obj->texture->width;
					int& height = intersections[j].obj->texture->height;
					int& column = intersections[j].column;
					int& scale = *intersections[j].scale;
					double& distance = intersections[j].distance;

					// calculate how many screen pixels takes one pixel from texture
					double scale_ratio_y = screen_height / distance * DISTANCE_RATIO_CONST * scale;


					double curr_start_y = (screen_height - scale_ratio_y) / 2;

					sf::Texture texture(*texture_ptr);
					sf::Sprite texture_line(texture);
					texture_line.setTextureRect(sf::Rect(sf::Vector2(column, 0), sf::Vector2(1, height)));
					texture_line.setScale(sf::Vector2((float)scale_ratio_x, (float)scale_ratio_y / float(height)));
					texture_line.setPosition(sf::Vector2((float)curr_start_x, (float)curr_start_y));
					screen.draw(texture_line);
				}
			}
			curr_start_x += scale_ratio_x;
		}
		screen.display();
		auto Updated_image = screen.getTexture().copyToImage();
		auto ptr = Updated_image.getPixelsPtr();
		std::copy(ptr, ptr + screen_width * screen_height * 4, output_pixels);
	}
	__declspec(dllexport) void* __cdecl create_texture_from_memory(
		std::uint8_t* pixels, 
		int width, 
		int height
	) {
		sf::Image* image = new sf::Image(sf::Vector2u(width, height), pixels);
		return static_cast<void*>(image);
	}
}