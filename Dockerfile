# Dockerfile for Odoo 18 with Custom Addons
FROM odoo:18.0

# Maintainer
LABEL maintainer="pakelkdrona@gmail.com"
LABEL description="Odoo 18 with API Training Course and custom modules"

# Set user to root for file operations
USER root

# Copy custom addons
COPY --chown=odoo:odoo ./addons /mnt/extra-addons

# Switch back to odoo user
USER odoo

# Expose Odoo ports
EXPOSE 8069 8072

# Default command (inherited from base image)
# CMD ["odoo"]
